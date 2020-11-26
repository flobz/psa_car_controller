import json
import re
import traceback
import uuid
from copy import copy
from datetime import datetime
from http import HTTPStatus
from json import JSONEncoder
from hashlib import md5
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation
import paho.mqtt.client as mqtt
from requests import Response
import psa_connectedcar as psac
from psa_connectedcar import ApiClient
from psa_connectedcar.rest import ApiException
from MyLogger import logger

oauth_urls = {'clientsB2COpel': 'https://idpcvs.opel.com/am/oauth2/access_token',
              'clientsB2CPeugeot': 'https://idpcvs.peugeot.com/am/oauth2/access_token',
              'default': 'https://idpcvs.peugeot.com/am/oauth2/access_token'}
authorize_service = "https://api.mpsa.com/api/connectedcar/v2/oauth/authorize"
remote_url = "https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token?client_id="
scopes = ['openid profile']
MQTT_SERVER = "mwa.mpsa.com"
default_ream = 'clientsB2CPeugeot'


class OpenIdCredentialManager(CredentialManager):
    def _grant_password_request(self, login: str, password: str, realm: str) -> dict:
        return dict(grant_type='password',
                    username=login,
                    scope=' '.join(self.service_information.scopes),
                    password=password, realm=realm)

    def init_with_user_credentials(self, login: str, password: str, realm: str):
        self._token_request(self._grant_password_request(login, password, realm), True)

    @staticmethod
    def _is_token_expired(response: Response) -> bool:
        if response.status_code == HTTPStatus.UNAUTHORIZED.value:
            logger.info("token expired, renew")
            try:
                json_data = response.json()
                return json_data.get('moreInformation') == 'Token is invalid'
            except ValueError:
                return False
        else:
            return False


class Oauth2PSACCApiConfig(psac.Configuration):
    def set_refresh_callback(self, callback):
        self.refresh_callback = callback


class OauthAPIClient(ApiClient):
    def call_api(self, resource_path, method,
                 path_params=None, query_params=None, header_params=None,
                 body=None, post_params=None, files=None,
                 response_type=None, auth_settings=None, async_req=None,
                 _return_http_data_only=None, collection_formats=None,
                 _preload_content=True, _request_timeout=None):
        for x in range(0, 2):
            try:
                if not async_req:
                    return self._ApiClient__call_api(resource_path, method,
                                                     path_params, query_params, header_params,
                                                     body, post_params, files,
                                                     response_type, auth_settings,
                                                     _return_http_data_only, collection_formats,
                                                     _preload_content, _request_timeout)
                else:
                    thread = self.pool.apply_async(self.__call_api, (resource_path,
                                                                     method, path_params, query_params,
                                                                     header_params, body,
                                                                     post_params, files,
                                                                     response_type, auth_settings,
                                                                     _return_http_data_only,
                                                                     collection_formats,
                                                                     _preload_content, _request_timeout))
                return thread
            except ApiException as e:
                if e.reason == 'Unauthorized':
                    self.configuration.refresh_callback()
                else:
                    raise e


def correlation_id(date):
    date_str = date.strftime("%Y%m%d%H%M%S%f")[:-3]
    uuid_str = str(uuid.uuid4()).replace("-", "")
    correlation_id = uuid_str + date_str
    return correlation_id


class MyPSACC:
    vehicles_url = "https://idpcvs.peugeot.com/api/connectedcar/v2/oauth/authorize"

    def connect(self, user, password, realm):
        self.manager.init_with_user_credentials(user, password, realm)

    def __init__(self, refresh_token, client_id, client_secret, remote_refresh_token, customer_id, proxies=None,
                 realm=default_ream):
        self.service_information = ServiceInformation(authorize_service,
                                                      self.get_oauth_url(realm),
                                                      client_id,
                                                      client_secret,
                                                      scopes, False)
        self.client_id = client_id
        self.manager = OpenIdCredentialManager(self.service_information)
        self.api_config = Oauth2PSACCApiConfig()
        self.api_config.set_refresh_callback(self.manager._refresh_token)
        self.manager.refresh_token = refresh_token
        self.remote_refresh_token = remote_refresh_token
        self.remote_access_token = None
        self.vehicles_list = None
        self.setProxies(proxies)
        self.customer_id = customer_id
        self._confighash = None
        self.realm = realm
        self.api_config.verify_ssl = False
        self.api_config.api_key['client_id'] = self.client_id
        self.api_config.api_key['x-introspect-realm'] = self.realm
        self.headers = {
                        "x-introspect-realm": realm,
                        "accept": "application/hal+json",
                    }

    @staticmethod
    def get_oauth_url(realm: str):
        if realm in oauth_urls.keys():
            return oauth_urls[realm]
        return oauth_urls['default']

    def refresh_token(self):
        self.manager._refresh_token()

    def api(self) -> psac.VehiclesApi:
        self.api_config.access_token = self.manager._access_token
        api_instance = psac.VehiclesApi(OauthAPIClient(self.api_config))
        return api_instance

    def setProxies(self, proxies):
        if proxies is None:
            self._proxies = dict(http='', https='')
            self.api_config.proxy = None
        else:
            self._proxies = proxies
            self.api_config.proxy = proxies['http']
        self.manager.proxies = self._proxies

    def get_vehicle_info(self, vin):
        res = self.api().get_vehicle_status(self.get_vehicle_id_with_vin(vin))
        # retry
        if res is None:
            res = self.api().get_vehicle_status(self.get_vehicle_id_with_vin(vin))
        return res

    # monitor doesn't seem to work
    def newMonitor(self, vin, body):
        res = self.manager.post("https://api.groupe-psa.com/connectedcar/v4/user/vehicles/" + self.vehicles_list[vin][
            "id"] + "/status?client_id=" + self.client_id, headers=MyPSACC.headers, data=body)
        data = res.json()
        return data

    def get_vehicles(self):
        res = self.api().get_vehicles_by_device()
        self.vehicles_list = {}
        for vehicle in res.embedded.vehicles:
            vin = vehicle.vin
            self.vehicles_list[vin] = {"id": vehicle.id}
        return self.vehicles_list

    def get_vehicle_id_with_vin(self, vin):
        return self.vehicles_list[vin]["id"]

    def getVIN(self):
        if self.vehicles_list is None:
            self.get_vehicles()
        return list(self.vehicles_list.keys())

    def get_remote_access_token(self, password):
        res = self.manager.post(remote_url + self.client_id,
                                json={"grant_type": "password", "password": password},
                                headers=self.headers)
        data = res.json()
        self.remote_access_token = data["access_token"]
        self.remote_refresh_token = data["refresh_token"]
        return res

    def refresh_remote_token(self):
        res = self.manager.post(remote_url + self.client_id,
                                json={"grant_type": "refresh_token", "refresh_token": self.remote_refresh_token},
                                headers=self.headers)
        data = res.json()
        logger.debug(f"refresh_remote_token: {data}")
        self.remote_access_token = data["access_token"]
        self.remote_refresh_token = data["refresh_token"]
        return data["access_token"], data["refresh_token"]

    def on_mqtt_connect(self, client, userdata, rc, a):
        try:
            logger.info("Connected with result code " + str(rc))
            topics = ["psa/RemoteServices/to/cid/" + self.customer_id + "/#"]
            for vin in self.getVIN():
                topics.append("psa/RemoteServices/events/MPHRTServices/" + vin + "/#")
            for topic in topics:
                client.subscribe(topic)
                logger.info("subscribe to " + topic)
        except:
            traceback.print_exc()

    def on_mqtt_disconnect(self, client, userdata, rc):
        try:
            logger.warn("Disconnected with result code " + str(rc))
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            logger.warn(mqtt.error_string(rc))
        except:
            traceback.print_exc()

    def on_mqtt_message(self, client, userdata, msg):
        logger.info(f"mqtt msg {msg.topic} {str(msg.payload)}")
        try:
            data = json.loads(msg.payload)
            if data["return_code"] == "0":
                return
            elif data["return_code"] == "400":
                self.manager._refresh_token()
                self.refresh_remote_token()
                logger.info("retry last request")
            else:
                logger.error(f'{data["return_code"]} : {data["reason"]}')
        except:
            logger.debug("mqtt msg hasn't return code")

    def start_mqtt(self):
        self.refresh_remote_token()
        self.mqtt_client = mqtt.Client(clean_session=True, protocol=mqtt.MQTTv311)
        self.mqtt_client.tls_set_context()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        self.mqtt_client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", self.remote_access_token)
        self.mqtt_client.connect(MQTT_SERVER, 8885, 60)
        self.mqtt_client.loop_start()
        return self.mqtt_client.is_connected()

    def mqtt_request(self, vin, req_parameters):
        date = datetime.now()
        date_f = "%Y-%m-%dT%H:%M:%SZ"
        date_str = date.strftime(date_f)
        data = {"access_token": self.remote_access_token, "customer_id": self.customer_id,
                "correlation_id": correlation_id(date), "req_date": date_str, "vin": vin,
                "req_parameters": req_parameters}

        return json.dumps(data)

    def get_charge_hour(self, vin):
        reg = r"PT([0-9]{1,2})H([0-9]{1,2})?"
        data = self.get_vehicle_info(vin)
        hour_str = data.energy[0]['charging']['nextDelayedTime']
        hour = re.findall(reg, hour_str)[0]
        h = int(hour[0])
        if hour[1] == '':
            m = 0
        else:
            m = hour[1]
        return h, m

    def get_charge_status(self, vin):
        data = self.get_vehicle_info(vin)
        status = data.energy[0]['charging']['status']
        return status

    def veh_charge_request(self, vin, hour, miinute, charge_type):
        # todo consider actual state before change the hour
        msg = self.mqtt_request(vin, {"program": {"hour": hour, "minute": miinute}, "type": charge_type})
        logger.info(msg)
        self.mqtt_client.publish("psa/RemoteServices/from/cid/" + self.customer_id + "/VehCharge", msg)

    def change_charge_hour(self, vin, hour, miinute):
        # todo consider actual state before change the hour
        self.veh_charge_request(vin, hour, miinute, "delayed")
        return True

    def charge_now(self, vin, now):
        if now:
            charge_type = "immediate"
        else:
            charge_type = "delayed"
        hour, minute = self.get_charge_hour(vin)
        self.veh_charge_request(vin, hour, minute, charge_type)
        return True

    def horn(self, vin, count):
        msg = self.mqtt_request(vin, {"nb_horn": count, "action": "activate"})
        logger.info(msg)
        self.mqtt_client.publish("psa/RemoteServices/from/cid/" + self.customer_id + "/Horn", msg)

    def lights(self, vin, duration: int):
        msg = self.mqtt_request(vin, {"action": "activate", "duration": duration})
        logger.info(msg)
        self.mqtt_client.publish("psa/RemoteServices/from/cid/" + self.customer_id + "/Lights", msg)

    def wakeup(self, vin):
        msg = self.mqtt_request(vin, {"action": "state"})
        logger.info(msg)
        self.mqtt_client.publish("psa/RemoteServices/from/cid/" + self.customer_id + "/VehCharge/state", msg)
        return True

    def lock_door(self, vin, lock: bool):
        if lock:
            value = "lock"
        else:
            value = "unlock"

        msg = self.mqtt_request(vin, {"action": value})
        logger.info(msg)
        self.mqtt_client.publish("psa/RemoteServices/from/cid/" + self.customer_id + "/Doors", msg)
        return True

    def preconditioning(self, vin, activate: bool):
        if activate:
            value = "activate"
        else:
            value = "deactivate"
        msg = self.mqtt_request(vin, {"asap": value, "programs": {
            "program1": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
            "program2": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
            "program3": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
            "program4": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0}}})
        logger.info(msg)
        self.mqtt_client.publish("psa/RemoteServices/from/cid/" + self.customer_id + "/ThermalPrecond", msg)
        return True

    def save_config(self, name="config.json", force=False):
        config_str = json.dumps(self, cls=MyPuegeotEncoder, sort_keys=True, indent=4).encode("utf8")
        new_hash = md5(config_str).hexdigest()
        if force or self._confighash != new_hash:
            with open(name, "wb") as f:
                f.write(config_str)
            self._confighash = new_hash
            logger.info("save config change")

    def load_config(name="config.json"):
        with open(name, "r") as f:
            str = f.read()
            return MyPSACC(**json.loads(str))


class MyPuegeotEncoder(JSONEncoder):
    def default(self, mp: MyPSACC):
        data = copy(mp.__dict__)
        mpd = {}
        mpd["proxies"] = data["_proxies"]
        mpd["refresh_token"] = mp.manager.refresh_token
        mpd["client_secret"] = mp.service_information.client_secret
        for el in ["client_id", "realm", "remote_refresh_token","customer_id"]:
            mpd[el] = data[el]
        return mpd
