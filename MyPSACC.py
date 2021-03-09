import json
import re
import threading
import traceback
import uuid
from copy import copy
from datetime import datetime
from http import HTTPStatus
from json import JSONEncoder
from hashlib import md5
from time import sleep

import requests
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation
import paho.mqtt.client as mqtt
from requests import Response

import psa_connectedcar as psac
from Car import Cars, Car
from ecomix import Ecomix
from otp.Otp import load_otp, new_otp_session, save_otp
from psa_connectedcar import ApiClient
from psa_connectedcar.rest import ApiException
from MyLogger import logger
from threading import Semaphore, Timer
from functools import wraps

from web.db import get_db
from geojson import Feature, Point, FeatureCollection
from geojson import dumps as geo_dumps

oauhth_url = {"clientsB2CPeugeot": "https://idpcvs.peugeot.com/am/oauth2/access_token",
              "clientsB2CCitroen": "https://idpcvs.citroen.com/am/oauth2/access_token",
              "clientsB2CDS": "https://idpcvs.driveds.com/am/oauth2/access_token",
              "clientsB2COpel": "https://idpcvs.opel.com/am/oauth2/access_token",
              "clientsB2CVauxhall": "https://idpcvs.vauxhall.co.uk/am/oauth2/access_token"}

authorize_service = "https://api.mpsa.com/api/connectedcar/v2/oauth/authorize"
remote_url = "https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token?client_id="
scopes = ['openid profile']
MQTT_SERVER = "mwa.mpsa.com"
MQTT_REQ_TOPIC = "psa/RemoteServices/from/cid/"
MQTT_RESP_TOPIC = "psa/RemoteServices/to/cid/"
MQTT_EVENT_TOPIC = "psa/RemoteServices/events/MPHRTServices/"
MQTT_TOKEN_TTL = 890


# add method to class Energy
def get_energy(self, energy_type):
    for energy in self._energy:
        if energy.type == energy_type:
            return energy
    return psac.models.energy.Energy(charging=psac.models.energy_charging.EnergyCharging())


psac.models.status.Status.get_energy = get_energy


def rate_limit(limit, every):
    def limit_decorator(fn):
        semaphore = Semaphore(limit)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            semaphore.acquire()
            try:
                return fn(*args, **kwargs)
            finally:  # don't catch but ensure semaphore release
                timer = Timer(every, semaphore.release)
                timer.setDaemon(True)  # allows the timer to be canceled on exit
                timer.start()

        return wrapper

    return limit_decorator


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
        for attempt in range(0, 2):
            try:
                if not async_req:
                    return self._ApiClient__call_api(resource_path, method,
                                                     path_params, query_params, header_params,
                                                     body, post_params, files,
                                                     response_type, auth_settings,
                                                     _return_http_data_only, collection_formats,
                                                     _preload_content, _request_timeout)
                return self.pool.apply_async(self.__call_api, (resource_path,
                                                               method, path_params, query_params,
                                                               header_params, body,
                                                               post_params, files,
                                                               response_type, auth_settings,
                                                               _return_http_data_only,
                                                               collection_formats,
                                                               _preload_content, _request_timeout))
            except ApiException as e:
                if e.reason == 'Unauthorized':
                    self.configuration.refresh_callback()
                else:
                    raise e


def correlation_id(date):
    date_str = date.strftime("%Y%m%d%H%M%S%f")[:-3]
    uuid_str = str(uuid.uuid4()).replace("-", "")
    correlationId = uuid_str + date_str
    return correlationId


class MyPSACC:
    vehicles_url = "https://idpcvs.peugeot.com/api/connectedcar/v2/oauth/authorize"

    def connect(self, user, password):
        self.manager.init_with_user_credentials(user, password, self.realm)

    def __init__(self, refresh_token, client_id, client_secret, remote_refresh_token, customer_id, realm, country_code,
                 proxies=None, weather_api=None):
        self.realm = realm
        self.service_information = ServiceInformation(authorize_service,
                                                      oauhth_url[self.realm],
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
        self.vehicles_list = Cars.load_cars()
        self.setProxies(proxies)
        self.customer_id = customer_id
        self._confighash = None
        self.api_config.verify_ssl = False
        self.api_config.api_key['client_id'] = self.client_id
        self.api_config.api_key['x-introspect-realm'] = self.realm
        self.headers = {
            "x-introspect-realm": realm,
            "accept": "application/hal+json",
            "User-Agent": "okhttp/4.8.0",
        }
        self.remote_token_last_update = None
        self._record_enabled = False
        self.otp = None
        self.weather_api = weather_api
        self.country_code = country_code
        self.mqtt_client = None
        self.precond_programs = {}
        self.info_callback = []
        self.info_refresh_rate = 120

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
        car = self.vehicles_list.get_car_by_vin(vin)
        for attempt in range(0, 2):
            res = self.api().get_vehicle_status(car.vehicle_id, extension=["odometer"])
            if res is not None:
                car.status = res
                if self._record_enabled:
                    self.record_info(vin, res)
                break
        return res

    def refresh_vehicle_info(self):
        if self.info_refresh_rate is not None:
            while True:
                sleep(self.info_refresh_rate)
                logger.info("refresh_vehicle_info")
                for car in self.vehicles_list:
                    self.get_vehicle_info(car.vin)
                for callback in self.info_callback:
                    callback()

    # monitor doesn't seem to work
    def newMonitor(self, vin, body):
        res = self.manager.post("https://api.groupe-psa.com/connectedcar/v4/user/vehicles/" +
                                self.vehicles_list.get_car_by_vin(vin).id + "/status?client_id=" + self.client_id,
                                headers=self.headers, data=body)
        data = res.json()
        return data

    def get_vehicles(self):
        res = self.api().get_vehicles_by_device()
        for vehicle in res.embedded.vehicles:
            vin = vehicle.vin
            self.vehicles_list.add(Car(vin, vehicle.id, vehicle.brand, vehicle.label))
        self.vehicles_list.save_cars()
        return self.vehicles_list

    def load_otp(self):
        otp_session = load_otp()
        if otp_session is None:
            self.get_sms_otp_code()
            otp_session = new_otp_session()
        return otp_session

    def get_sms_otp_code(self):
        res = self.manager.post(
            "https://api.groupe-psa.com/applications/cvs/v4/mobile/smsCode?client_id=" + self.client_id,
            headers={
                "Connection": "Keep-Alive",
                "User-Agent": "okhttp/4.8.0",
                "x-introspect-realm": self.realm
            })
        return res

    # 6 otp by day
    @rate_limit(6, 3600 * 24)
    def getOtpCode(self):
        otp_code = self.otp.getOtpCode()
        save_otp(self.otp)
        return otp_code

    def get_remote_access_token(self, password):
        res = self.manager.post(remote_url + self.client_id,
                                json={"grant_type": "password", "password": password},
                                headers=self.headers)
        data = res.json()
        self.remote_access_token = data["access_token"]
        self.remote_refresh_token = data["refresh_token"]
        return res

    def refresh_remote_token(self, force=False):
        if not force and self.remote_token_last_update is not None:
            last_update: datetime = self.remote_token_last_update
            if (datetime.now() - last_update).total_seconds() < MQTT_TOKEN_TTL:
                return None
        self.manager._refresh_token()
        res = self.manager.post(remote_url + self.client_id,
                                json={"grant_type": "refresh_token", "refresh_token": self.remote_refresh_token},
                                headers=self.headers)
        data = res.json()
        logger.debug("refresh_remote_token: %s", data)
        if "access_token" in data:
            self.remote_access_token = data["access_token"]
            self.remote_refresh_token = data["refresh_token"]
            self.remote_token_last_update = datetime.now()
        else:
            logger.error("can't refresh_remote_token: %s\n Create a new one", data)
            self.remote_token_last_update = datetime.now()
            otp_code = self.getOtpCode()
            res = self.get_remote_access_token(otp_code)
        self.mqtt_client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", self.remote_access_token)
        return res

    def on_mqtt_connect(self, client, userdata, rc, a):
        try:
            logger.info("Connected with result code %s", rc)
            topics = [MQTT_RESP_TOPIC + self.customer_id + "/#"]
            for car in self.vehicles_list:
                topics.append(MQTT_EVENT_TOPIC + car.vin)
            for topic in topics:
                client.subscribe(topic)
                logger.info("subscribe to %s", topic)
        except:
            logger.error(traceback.format_exc())

    def on_mqtt_disconnect(self, client, userdata, rc):
        try:
            logger.warning("Disconnected with result code %d", rc)
            if rc == 1:
                self.refresh_remote_token(force=True)
            else:
                logger.warning(mqtt.error_string(rc))
        except:
            logger.error(traceback.format_exc())

    def on_mqtt_message(self, client, userdata, msg):
        charge_not_detected = False
        try:
            logger.info("mqtt msg %s %s", msg.topic, msg.payload)
            data = json.loads(msg.payload)
            if msg.topic.startswith(MQTT_RESP_TOPIC):
                if "return_code" in data:
                    if data["return_code"] == "0":
                        pass
                    elif data["return_code"] == "400":
                        self.refresh_remote_token(force=True)
                        logger.error("retry last request, token was expired")
                    elif data["return_code"] == "300":
                        logger.error('%d', data["return_code"])
                    else:
                        logger.error('%s : %s', data["return_code"], data["reason"])
                else:
                    logger.debug("mqtt msg hasn't return code")
            if msg.topic.startswith(MQTT_EVENT_TOPIC):
                if data["charging_state"]['remaining_time'] != 0 and data["charging_state"]['rate'] == 0:
                    charge_not_detected = True
            elif msg.topic.endswith("/VehicleState"):
                try:
                    if data["resp_data"]["charging_state"]['remaining_time'] != 0 \
                            and data["resp_data"]["charging_state"]['rate'] == 0:
                        charge_not_detected = True
                    self.precond_programs[data["vin"]] = data["resp_data"]["precond_state"]["programs"]
                except KeyError:
                    pass
            if charge_not_detected:
                # fix a psa server bug where charge beginning without status api being properly updated
                logger.info("charge begin")
                sleep(60)
                self.wakeup(data["vin"])
        except:
            logger.error(traceback.format_exc())

    def start_mqtt(self):
        self.otp = self.load_otp()
        self.mqtt_client = mqtt.Client(clean_session=True, protocol=mqtt.MQTTv311)
        self.refresh_remote_token()
        self.mqtt_client.tls_set_context()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        self.mqtt_client.connect(MQTT_SERVER, 8885, 60)
        self.mqtt_client.loop_start()
        self.__keep_mqtt()
        return self.mqtt_client.is_connected()

    def __keep_mqtt(self):  # avoid token expiration
        timeout = 3600 * 24  # 1 day
        try:
            self.get_state(self.vehicles_list[0].vin)
        except:
            logger.warning("keep_mqtt error")
        threading.Timer(timeout, self.__keep_mqtt).start()

    def mqtt_request(self, vin, req_parameters):
        self.refresh_token()
        date = datetime.utcnow()
        date_f = "%Y-%m-%dT%H:%M:%SZ"
        date_str = date.strftime(date_f)
        data = {"access_token": self.remote_access_token, "customer_id": self.customer_id,
                "correlation_id": correlation_id(date), "req_date": date_str, "vin": vin,
                "req_parameters": req_parameters}

        return json.dumps(data)

    def get_charge_hour(self, vin):
        reg = r"PT([0-9]{1,2})H([0-9]{1,2})?"
        data = self.get_vehicle_info(vin)
        hour_str = data.get_energy('Electric').charging.next_delayed_time
        try:
            hour = re.findall(reg, hour_str)[0]
            h = int(hour[0])
            if hour[1] == '':
                m = 0
            else:
                m = hour[1]
            return h, m
        except IndexError:
            logger.error(traceback.format_exc())
            logger.error("Can't get charge hour: %s", hour_str)

    def get_charge_status(self, vin):
        data = self.get_vehicle_info(vin)
        status = data.get_energy('Electric').charging.status
        return status

    def veh_charge_request(self, vin, hour, miinute, charge_type):
        # todo consider actual state before change the hour
        msg = self.mqtt_request(vin, {"program": {"hour": hour, "minute": miinute}, "type": charge_type})
        logger.info(msg)
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/VehCharge", msg)

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
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/Horn", msg)

    def lights(self, vin, duration: int):
        msg = self.mqtt_request(vin, {"action": "activate", "duration": duration})
        logger.info(msg)
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/Lights", msg)

    @rate_limit(3, 60 * 20)
    def wakeup(self, vin):
        logger.info("ask wakeup to %s", vin)
        msg = self.mqtt_request(vin, {"action": "state"})
        logger.info(msg)
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/VehCharge/state", msg)
        return True

    # get state from server by mqtt
    def get_state(self, vin):
        logger.info("ask state to %s", vin)
        msg = self.mqtt_request(vin, {"action": "state"})
        logger.info(msg)
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/VehicleState", msg)
        return True

    def lock_door(self, vin, lock: bool):
        if lock:
            value = "lock"
        else:
            value = "unlock"

        msg = self.mqtt_request(vin, {"action": value})
        logger.info(msg)
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/Doors", msg)
        return True

    def preconditioning(self, vin, activate: bool):
        if activate:
            value = "activate"
        else:
            value = "deactivate"
        self.get_state(vin)
        sleep(2)  # wait for rep
        if vin in self.precond_programs:
            programs = self.precond_programs[vin]
        else:
            programs = {
                "program1": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
                "program2": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
                "program3": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
                "program4": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0}
            }
        msg = self.mqtt_request(vin, {"asap": value, "programs": programs})
        logger.info(msg)
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/ThermalPrecond", msg)
        return True

    def save_config(self, name="config.json", force=False):
        config_str = json.dumps(self, cls=MyPeugeotEncoder, sort_keys=True, indent=4).encode("utf8")
        new_hash = md5(config_str).hexdigest()
        if force or self._confighash != new_hash:
            with open(name, "wb") as f:
                f.write(config_str)
            self._confighash = new_hash
            logger.info("save config change")

    @staticmethod
    def load_config(name="config.json"):
        with open(name, "r") as f:
            config_str = f.read()
            config = dict(**json.loads(config_str))
            if "country_code" not in config:
                config["country_code"] = input("What is your country code ? (ex: FR, GB, DE, ES...)\n")
            return MyPSACC(**config)

    def set_record(self, value: bool):
        self._record_enabled = value

    def record_info(self, vin, status: psac.models.status.Status):
        longitude = status.last_position.geometry.coordinates[0]
        latitude = status.last_position.geometry.coordinates[1]
        date = status.last_position.properties.updated_at
        mileage = status.timed_odometer.mileage
        level = status.get_energy('Electric').level
        charging_status = status.get_energy('Electric').charging.status
        charge_date = status.get_energy('Electric').updated_at
        level_fuel = status.get_energy('Fuel').level
        moving = status.kinetic.moving
        logger.debug(
            "vin:%s longitude:%s latitude:%s date:%s mileage:%s level:%s charging_status:%s charge_date:%s level_fuel:"
            "%s moving:%s", vin, longitude, latitude, date, mileage, level, charging_status, charge_date, level_fuel,
            moving)
        conn = get_db()
        if mileage == 0:  # fix a bug of the api
            logger.error("The api return a wrong mileage for %s : %f", vin, mileage)
        else:
            if conn.execute("SELECT Timestamp from position where Timestamp=?", (date,)).fetchone() is None:
                temp = None
                if self.weather_api is not None:
                    try:
                        weather_rep = requests.get("https://api.openweathermap.org/data/2.5/onecall",
                                                   params={"lat": latitude, "lon": longitude,
                                                           "exclude": "minutely,hourly,daily,alerts",
                                                           "appid": self.weather_api,
                                                           "units": "metric"})
                        temp = weather_rep.json()["current"]["temp"]
                        logger.debug("Temperature :%fc", temp)
                    except:
                        logger.error("Unable to get temperature from openweathermap :%s", temp)

                if level_fuel == 0:  # fix fuel level not provided when car is off
                    try:
                        level_fuel = conn.execute(
                            "SELECT level_fuel FROM position WHERE level_fuel>0 AND VIN=? ORDER BY Timestamp DESC LIMIT 1",
                            (vin,)).fetchone()[0]
                        logger.info("level_fuel fixed with last real value %f for %s", level_fuel, vin)
                    except TypeError:
                        level_fuel = None
                        logger.info("level_fuel unfixed for %s", vin)

                conn.execute(
                    "INSERT INTO position(Timestamp,VIN,longitude,latitude,mileage,level,level_fuel,moving,temperature) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (date, vin, longitude, latitude, mileage, level, level_fuel, moving, temp))

                conn.commit()
                logger.info("new position recorded for %s", vin)
                res = conn.execute(
                    "SELECT Timestamp,mileage,level from position ORDER BY Timestamp DESC LIMIT 3;").fetchall()
                # Clean DB
                if len(res) == 3:
                    if res[0]["mileage"] == res[1]["mileage"] == res[2]["mileage"]:
                        if res[0]["level"] == res[1]["level"] == res[2]["level"]:
                            logger.debug("Delete duplicate line")
                            conn.execute("DELETE FROM position where Timestamp=?;", (res[1]["Timestamp"],))
                            conn.commit()
            else:
                logger.debug("position already saved")

        # todo handle battery status
        if charging_status == "InProgress":
            try:
                in_progress = conn.execute("SELECT stop_at FROM battery WHERE VIN=? ORDER BY start_at DESC limit 1",
                                           (vin,)).fetchone()[0] is None
            except TypeError:
                in_progress = False
            if not in_progress:
                res = conn.execute("INSERT INTO battery(start_at,start_level,VIN) VALUES(?,?,?)",
                                   (charge_date, level, vin))
                conn.commit()
        else:
            try:
                start_at, stop_at, start_level = conn.execute(
                    "SELECT start_at, stop_at, start_level from battery WHERE VIN=? ORDER BY start_at "
                    "DESC limit 1", (vin,)).fetchone()
                in_progress = stop_at is None
                if in_progress:
                    co2_per_kw = Ecomix.get_co2_per_kw(start_at, charge_date, latitude, longitude)
                    kw = (level - start_level) / 100 * self.vehicles_list.get_car_by_vin(vin).battery_power
                    res = conn.execute(
                        "UPDATE battery set stop_at=?, end_level=?, co2=?, kw=? WHERE start_at=? and VIN=?",
                        (charge_date, level, co2_per_kw, kw, start_at, vin))
                    conn.commit()
            except TypeError:
                logger.debug("battery table is empty")
            except:
                logger.debug("Error when saving status %s", traceback.format_exc())
        conn.close()

    @staticmethod
    def get_recorded_position():
        conn = get_db()
        res = conn.execute('SELECT * FROM position ORDER BY Timestamp')
        features_list = []
        for row in res:
            feature = Feature(geometry=Point((row["longitude"], row["latitude"])),
                              properties={"vin": row["vin"], "date": row["Timestamp"].strftime("%x %X"),
                                          "mileage": row["mileage"],
                                          "level": row["level"], "level_fuel": row["level_fuel"]})
            features_list.append(feature)
        feature_collection = FeatureCollection(features_list)
        conn.close()
        return geo_dumps(feature_collection, sort_keys=True)

    @staticmethod
    def get_chargings(mini=None, maxi=None):
        conn = get_db()
        if mini is not None:
            if maxi is not None:
                res = conn.execute("select * from battery WHERE start_at>=? and start_at<=?", (mini, maxi)).fetchall()
            else:
                res = conn.execute("select * from battery WHERE start_at>=?", (mini,)).fetchall()
        elif maxi is not None:
            res = conn.execute("select * from battery WHERE start_at<=?", (maxi,)).fetchall()
        else:
            res = conn.execute("select * from battery").fetchall()
        return tuple(map(dict, res))


class MyPeugeotEncoder(JSONEncoder):
    def default(self, mp: MyPSACC):
        data = copy(mp.__dict__)
        mpd = {"proxies": data["_proxies"], "refresh_token": mp.manager.refresh_token,
               "client_secret": mp.service_information.client_secret}
        for el in ["client_id", "realm", "remote_refresh_token", "customer_id", "weather_api", "country_code"]:
            mpd[el] = data[el]
        return mpd
