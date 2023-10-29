import json
import logging
import threading
from datetime import datetime
from os import environ
import time

import paho.mqtt.client as mqtt
from requests import RequestException

from psa_car_controller.psacc.model.car import Cars
from psa_car_controller.psa.AccountInformation import AccountInformation
from psa_car_controller.psa.RemoteCredentials import RemoteCredentials
from psa_car_controller.psa.constants import INPROGRESS, DEFAULT_PRECONDITIONING_PROGRAM, IMMEDIATE_CHARGE, \
    DELAYED_CHARGE, REMOTE_URL
from psa_car_controller.psa.mqtt_request import MQTTRequest
from psa_car_controller.psa.oauth import OpenIdCredentialManager
from psa_car_controller.common.utils import RateLimitException, rate_limit, parse_hour
from psa_car_controller.psa.otp.otp import ConfigException, save_otp, load_otp

logger = logging.getLogger(__name__)

MQTT_SERVER = "mwa.mpsa.com"
MQTT_RESP_TOPIC = "psa/RemoteServices/to/cid/"
MQTT_EVENT_TOPIC = "psa/RemoteServices/events/MPHRTServices/"
MQTT_TOKEN_TTL = 890


class RemoteClient:

    def __init__(self, account_info: AccountInformation, vehicles_list: Cars, manager: OpenIdCredentialManager,
                 remoteCredentials: RemoteCredentials):
        self.vehicles_list = vehicles_list
        self.remoteCredentials: RemoteCredentials = remoteCredentials
        self.manager = manager
        self.precond_programs = {}
        self.account_info = account_info
        self.headers = {
            "x-introspect-realm": self.account_info.realm,
            "accept": "application/hal+json",
            "User-Agent": "okhttp/4.8.0",
        }
        self.last_request = None
        self.mqtt_client = None
        self.otp = None

    def __on_mqtt_connect(self, client, userdata, result_code, _):  # pylint: disable=unused-argument
        logger.info("Connected with result code %s", result_code)
        topics = [MQTT_RESP_TOPIC + self.account_info.get_mqtt_customer_id() + "/#"]
        for car in self.vehicles_list:
            topics.append(MQTT_EVENT_TOPIC + car.vin)
        for topic in topics:
            client.subscribe(topic)
            logger.info("subscribe to %s", topic)

    def _on_mqtt_disconnect(self, client, userdata, result_code):  # pylint: disable=unused-argument
        logger.warning("Disconnected with result code %d", result_code)
        if result_code == 1:
            self._refresh_remote_token(force=True)
        else:
            logger.warning(mqtt.error_string(result_code))

    def _on_mqtt_message(self, client, userdata, msg):  # pylint: disable=unused-argument
        try:
            logger.info("mqtt msg received: %s %s", msg.topic, msg.payload)
            data = json.loads(msg.payload)
            charge_info = None
            if msg.topic.startswith(MQTT_RESP_TOPIC):
                if "return_code" not in data:
                    logger.debug("mqtt msg hasn't return code")
                elif data["return_code"] == "400":
                    self._refresh_remote_token(force=True)
                    if self.last_request:
                        logger.warning("last request is send again, token was expired")
                        last_request = self.last_request
                        self.last_request = None
                        self.publish(last_request, store=False)
                    else:
                        logger.error("Last request might have been send twice without success")
                elif data["return_code"] != "0":
                    logger.error('%s : %s', data["return_code"], data.get("reason", "?"))
            elif msg.topic.startswith(MQTT_EVENT_TOPIC):
                charge_info = data["charging_state"]
                programs = data["precond_state"].get("programs", None)
                if programs:
                    self.precond_programs[data["vin"]] = data["precond_state"]["programs"]
            self._fix_not_updated_api(charge_info, data["vin"])
        except KeyError:
            logger.exception("on_mqtt_message:")

    def _fix_not_updated_api(self, charge_info, vin):
        if charge_info is not None and (charge_info.get('remaining_time', 0) != 0 or charge_info.get('rate', 0) != 0):
            try:
                car = self.vehicles_list.get_car_by_vin(vin=vin)
                if car and car.status.get_energy('Electric').charging.status != INPROGRESS:
                    # fix a psa server bug where charge beginning without status api being properly updated
                    logger.warning("charge begin but API isn't updated")
                    time.sleep(60)
                    self.wakeup(vin)
            except (IndexError, AttributeError, RateLimitException):
                logger.exception("on_mqtt_message:")

    def start(self):
        if self.load_otp():
            self.mqtt_client = mqtt.Client(clean_session=True, protocol=mqtt.MQTTv311)
            if environ.get("MQTT_LOG", "0") == "1":
                self.mqtt_client.enable_logger(logger=logger)
            if self._refresh_remote_token():
                self.mqtt_client.tls_set_context()
                self.mqtt_client.on_connect = self.__on_mqtt_connect
                self.mqtt_client.on_message = self._on_mqtt_message
                self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
                self.mqtt_client.connect(MQTT_SERVER, 8885, 60)
                self.mqtt_client.loop_start()
                self.__keep_mqtt()
                return self.mqtt_client.is_connected()
        logger.error("Can't configure MQTT Client")
        return False

    def __keep_mqtt(self):  # avoid token expiration
        timeout = 3600 * 24  # 1 day
        if len(self.vehicles_list) > 0:
            try:
                self.wakeup(self.vehicles_list[0].vin)
            except RateLimitException:
                logger.exception("__keep_mqtt")
        t = threading.Timer(timeout, self.__keep_mqtt)
        t.daemon = True
        t.start()

    def veh_charge_request(self, vin, hour, minute, charge_type):
        msg = self.mqtt_request(vin, {"program": {"hour": hour, "minute": minute}, "type": charge_type}, "/VehCharge")
        logger.info("veh_charge_request: %s", msg)
        self.publish(msg)
        return msg

    def publish(self, mqtt_request: MQTTRequest, store=True):
        self._refresh_remote_token()
        message = mqtt_request.get_message_to_json(self.remoteCredentials.access_token)
        logger.debug("%s %s", mqtt_request.topic, message)
        self.mqtt_client.publish(mqtt_request.topic, message)
        if store:
            self.last_request = mqtt_request

    def mqtt_request(self, vin, req_parameters, topic):
        return MQTTRequest(topic, vin, req_parameters, self.account_info.get_mqtt_customer_id())

    def _refresh_remote_token(self, force=False):
        bad_remote_token = self.remoteCredentials.refresh_token is None
        if not force and not bad_remote_token and self.remoteCredentials.last_update:
            last_update: datetime = self.remoteCredentials.last_update
            if (datetime.now() - last_update).total_seconds() < MQTT_TOKEN_TTL:
                return True
        try:
            self.manager.refresh_token_now()
            if bad_remote_token:
                logger.error("remote_refresh_token isn't defined")
            else:
                res = self.manager.post(REMOTE_URL + self.account_info.client_id,
                                        json={"grant_type": "refresh_token",
                                              "refresh_token": self.remoteCredentials.refresh_token},
                                        headers=self.headers)
                data = res.json()
                logger.debug("refresh_remote_token: %s", data)
                if "access_token" in data:
                    self.remoteCredentials.access_token = data["access_token"]
                    self.remoteCredentials.refresh_token = data["refresh_token"]
                    bad_remote_token = False
                else:
                    logger.error("can't refresh_remote_token: %s\n Create a new one", data)
                    bad_remote_token = True
            if bad_remote_token:
                otp_code = self.get_otp_code()
                self._get_remote_access_token(otp_code)
            self.remote_token_last_update = datetime.now()
            self.mqtt_client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", self.remoteCredentials.access_token)
            return True
        except (RequestException, RateLimitException, KeyError) as e:
            logger.exception("Can't refresh remote token %s", e)
            time.sleep(60)
            return False

    def get_sms_otp_code(self):
        res = self.manager.post(
            "https://api.groupe-psa.com/applications/cvs/v4/mobile/smsCode?client_id=" + self.account_info.client_id,
            headers=self.headers)
        return res

    # 6 otp by day
    @rate_limit(6, 3600 * 24)
    def get_otp_code(self):
        try:
            otp_code = self.otp.get_otp_code()
        except ConfigException:
            logger.exception("get_otp_code:")
            self.load_otp(force_new=True)
            otp_code = self.otp.get_otp_code()
        save_otp(self.otp)
        return otp_code

    def _get_remote_access_token(self, password):
        res = self.manager.post(REMOTE_URL + self.account_info.client_id,
                                json={"grant_type": "password", "password": password},
                                headers=self.headers)
        data = res.json()
        self.remoteCredentials.access_token = data["access_token"]
        self.remoteCredentials.refresh_token = data["refresh_token"]
        return res

    def horn(self, vin, count):
        msg = self.mqtt_request(vin, {"nb_horn": count, "action": "activate"}, "/Horn")
        logger.info(msg)
        self.mqtt_client.publish(msg)

    def lights(self, vin, duration: int):
        msg = self.mqtt_request(vin, {"action": "activate", "duration": duration}, "/Lights")
        logger.info(msg)
        self.publish(msg)

    @rate_limit(6, 60 * 20)
    def wakeup(self, vin):
        logger.info("ask wakeup to %s", vin)
        msg = self.mqtt_request(vin, {"action": "state"}, "/VehCharge/state")
        logger.info(msg)
        self.publish(msg)
        return True

    def lock_door(self, vin, lock: bool):
        if lock:
            value = "lock"
        else:
            value = "unlock"

        msg = self.mqtt_request(vin, {"action": value}, "/Doors")
        logger.info(msg)
        self.publish(msg)
        return True

    def preconditioning(self, vin, activate: bool):
        if activate:
            value = "activate"
        else:
            value = "deactivate"
        if vin in self.precond_programs:
            programs = self.precond_programs[vin]
        else:
            programs = DEFAULT_PRECONDITIONING_PROGRAM
        msg = self.mqtt_request(vin, {"asap": value, "programs": programs}, "/ThermalPrecond")
        logger.info("Preconditioning: %s", msg)
        self.publish(msg)
        return True

    def load_otp(self, force_new=False):
        otp_session = load_otp()
        if otp_session is None or force_new:
            logger.error("Please redo otp config")
            return False
        self.otp = otp_session
        return True

    def change_charge_hour(self, vin, hour, miinute):
        self.veh_charge_request(vin, hour, miinute, DELAYED_CHARGE)
        return True

    def charge_now(self, vin, now):
        if now:
            charge_type = IMMEDIATE_CHARGE
        else:
            charge_type = DELAYED_CHARGE
        hour, minute = self.get_charge_hour(vin)
        res = self.veh_charge_request(vin, hour, minute, charge_type)
        logger.info("charge_now: %s", res)
        return True

    def get_charge_hour(self, vin):
        hour_str = self.vehicles_list.get_car_by_vin(vin).status.get_energy('Electric').charging.next_delayed_time
        try:
            return parse_hour(hour_str)[:2]
        except IndexError:
            logger.exception("Can't get charge hour: %s", hour_str)
            return None
