import json
import threading
import traceback
from copy import copy
from datetime import datetime, timedelta
from hashlib import md5
from time import sleep

import pytz

from MyPSACC import MyPSACC
from MyLogger import logger

DISCONNECTED = "Disconnected"
INPROGRESS = "InProgress"
FAILURE = "Failure"
STOPPED = "Stopped"
FINISHED = "Finished"


class ChargeControl:
    MQTT_TIMEOUT = 60

    def __init__(self, psacc: MyPSACC, vin, percentage_threshold, stop_hour):
        self.vin = vin
        self.percentage_threshold = percentage_threshold
        self.set_stop_hour(stop_hour)
        self.psacc = psacc
        self.retry_count = 0

    def set_stop_hour(self, stop_hour):
        if stop_hour is None or stop_hour == [0, 0]:
            self._stop_hour = None
            self._next_stop_hour = None
        else:
            self._stop_hour = stop_hour
            self._next_stop_hour = datetime.now().replace(hour=stop_hour[0], minute=stop_hour[1], second=0)
            if self._next_stop_hour < datetime.now():
                self._next_stop_hour += timedelta(days=1)

    def get_stop_hour(self):
        return self._stop_hour

    def control_charge_with_ack(self, charge: bool):
        self.psacc.charge_now(self.vin, charge)
        self.retry_count += 1
        sleep(ChargeControl.MQTT_TIMEOUT)
        vehicle_status = self.psacc.get_vehicle_info(self.vin)
        status = vehicle_status.get_energy('Electric').charging.status
        if status in (FINISHED, DISCONNECTED):
            logger.warning("Car state isn't compatible with charging %s", status)
        if (status == INPROGRESS) != charge:
            logger.warning("retry to control the charge of %s", self.vin)
            self.psacc.charge_now(self.vin, charge)
            self.retry_count += 1
            return False
        self.retry_count = 0
        return True

    def force_update(self):
        # force update if the car doesn't send info during 10 minutes
        last_update = self.psacc.vehicles_list.get_car_by_vin(self.vin).get_status().get_energy('Electric').updated_at
        if (datetime.utcnow().replace(tzinfo=pytz.UTC) - last_update).total_seconds() > 60 * 10:
            self.psacc.wakeup(self.vin)

    def process(self):
        now = datetime.now()
        try:
            vehicle_status = self.psacc.vehicles_list.get_car_by_vin(self.vin).get_status()
            status = vehicle_status.get_energy('Electric').charging.status
            level = vehicle_status.get_energy('Electric').level
            logger.info("charging status of %s is %s, battery level: %d", self.vin, status, level)
            if status == "InProgress":
                self.force_update()
                if level >= self.percentage_threshold and self.retry_count < 2:
                    logger.info("Charge threshold is reached, stop the charge")
                    self.control_charge_with_ack(False)
                elif self._next_stop_hour is not None:
                    if self._next_stop_hour < now:
                        self._next_stop_hour += timedelta(days=1)
                        logger.info("it's time to stop the charge")
                        self.control_charge_with_ack(False)
                    else:
                        next_in_second = (self._next_stop_hour - now).total_seconds()
                        if next_in_second < self.psacc.info_refresh_rate:
                            periodicity = next_in_second
                            thread = threading.Timer(periodicity, self.process)
                            thread.setDaemon(True)
                            thread.start()
            else:
                if self._next_stop_hour < now:
                    self._next_stop_hour += timedelta(days=1)
                self.retry_count = 0
        except AttributeError:
            logger.error("Probably can't retrieve all information from API: %s", traceback.format_exc())
        except:
            logger.error(traceback.format_exc())

    def get_dict(self):
        chd = copy(self.__dict__)
        chd.pop("psacc")
        return chd


class ChargeControls(dict):

    def __init__(self):
        super().__init__()
        self._config_hash = None

    def save_config(self, name="charge_config.json", force=False):
        chd = {}
        charge_control: ChargeControl
        for charge_control in self.values():
            chd[charge_control.vin] = {"percentage_threshold": charge_control.percentage_threshold,
                                       "stop_hour": charge_control.get_stop_hour()}
        config_str = json.dumps(chd, sort_keys=True, indent=4).encode('utf-8')
        new_hash = md5(config_str).hexdigest()
        if force or self._config_hash != new_hash:
            with open(name, "wb") as f:
                f.write(config_str)
            self._config_hash = new_hash
            logger.info("save config change")

    @staticmethod
    def load_config(psacc: MyPSACC, name="charge_config.json"):
        with open(name, "r") as f:
            config_str = f.read()
            chd = json.loads(config_str)
            charge_control_list = ChargeControls()
            for vin, el in chd.items():
                charge_control_list[vin] = ChargeControl(psacc, vin, **el)
            return charge_control_list

    def get(self, vin) -> ChargeControl:
        try:
            return self[vin]
        except KeyError:
            pass

    def init(self):
        for charge_control in self.values():
            charge_control.psacc.info_callback.append(charge_control.process)
