import json
import logging
from datetime import datetime
from json.decoder import JSONDecodeError

import requests

from psa_car_controller.psacc.model.car import Car

logger = logging.getLogger(__name__)
TIMEOUT_IN_S = 10


class Abrp:
    api_key = "1e28ad14-df16-49f0-97da-364c9154b44a"
    url = "https://api.iternio.com/1/tlm/send"

    def __init__(self, token: str = "", abrp_enable_vin=None):
        if abrp_enable_vin is None:
            abrp_enable_vin = []
        self.token = token
        self.abrp_enable_vin = set(abrp_enable_vin)
        self.proxies = None

    def enable_abrp(self, vin, enable):
        if enable:
            self.abrp_enable_vin.add(vin)
        else:
            self.abrp_enable_vin.discard(vin)

    def call(self, car: Car, ext_temp: float = None):
        try:
            if self.token is None or len(self.token) == 0:
                logger.debug("No abrp token provided")
            elif car.vin in self.abrp_enable_vin:
                energy = car.status.get_energy('Electric')

                if energy.level is None:
                    logger.debug("No energy level available")
                    return False

                tlm = {"utc": int(datetime.timestamp(energy.updated_at)),
                       "soc": energy.level,
                       "speed": getattr(car.status.kinetic, "speed", None),
                       "car_model": car.get_abrp_name(),
                       "current": car.status.battery.current,
                       "is_charging": energy.charging.status == "InProgress",
                       "lat": car.status.last_position.geometry.coordinates[1],
                       "lon": car.status.last_position.geometry.coordinates[0],
                       "power": energy.consumption
                       }
                if ext_temp is not None:
                    tlm["ext_temp"] = ext_temp
                params = {"tlm": json.dumps(tlm), "token": self.token, "api_key": self.api_key}
                response = requests.request("POST", self.url, params=params, proxies=self.proxies,
                                            verify=self.proxies is None, timeout=TIMEOUT_IN_S)
                logger.debug(response.text)
                try:
                    return json.loads(response.text)["status"] == "ok"
                except (JSONDecodeError, KeyError):
                    logger.error("Bad response from ABRP API: %s", response.text)
                    return False
        except (AttributeError, IndexError, ValueError):
            logger.exception("abrp:")
        return False

    def __iter__(self):
        yield "abrp_enable_vin", list(self.abrp_enable_vin)
        yield "token", self.token
