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
from typing import List

import psa_connectedcar as psac
from Trip import Trip
from ecomix import Ecomix
from otp.Otp import load_otp, new_otp_session, save_otp
from psa_connectedcar import ApiClient
from psa_connectedcar.rest import ApiException
from MyLogger import logger
from threading import Semaphore, Timer
from functools import wraps
import sqlite3

from web.db import get_db

ENERGY_CAPACITY = {'SUV 3008':    {'BATTERY_POWER': 10.8, 'FUEL_CAPACITY': 43},
                   'C5 Aircross': {'BATTERY_POWER': 10.8, 'FUEL_CAPACITY': 43},
                   '208':         {'BATTERY_POWER': 46,   'FUEL_CAPACITY': 0},     # to be verified by an e208 owner - to be changed in ENERGY_CAPACITY and in get_trip function vehicle_model default value
                  }

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

    def connect(self, user, password):
        self.manager.init_with_user_credentials(user, password, self.realm)

    def __init__(self, refresh_token, client_id, client_secret, remote_refresh_token, customer_id, realm, proxies=None, weather_api = None):
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
        self.vehicles_list = None
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
        res = self.api().get_vehicle_status(self.get_vehicle_id_with_vin(vin), extension=["odometer"])
        # retry
        if res is None:
            res = self.api().get_vehicle_status(self.get_vehicle_id_with_vin(vin), extension=["odometer"])
        if self._record_enabled:
            self.record_info(vin, res)
        return res

    # monitor doesn't seem to work
    def newMonitor(self, vin, body):
        res = self.manager.post("https://api.groupe-psa.com/connectedcar/v4/user/vehicles/" + self.vehicles_list[vin][
            "id"] + "/status?client_id=" + self.client_id, headers=self.headers, data=body)
        data = res.json()
        return data

    def get_vehicles(self):
        res = self.api().get_vehicles_by_device()
        self.vehicles_list = {}
        for vehicle in res.embedded.vehicles:
            vin = vehicle.vin
            self.vehicles_list[vin] = {"id": vehicle.id,"brand": vehicle.brand, "label": vehicle.label}
        return self.vehicles_list

    def get_vehicle_id_with_vin(self, vin):
        return self.vehicles_list[vin]["id"]

    def getVIN(self):
        if self.vehicles_list is None:
            self.get_vehicles()
        return list(self.vehicles_list.keys())

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
                return
        self.manager._refresh_token()
        res = self.manager.post(remote_url + self.client_id,
                                json={"grant_type": "refresh_token", "refresh_token": self.remote_refresh_token},
                                headers=self.headers)
        data = res.json()
        logger.debug(f"refresh_remote_token: {data}")
        if "access_token" in data:
            self.remote_access_token = data["access_token"]
            self.remote_refresh_token = data["refresh_token"]
            self.remote_token_last_update = datetime.now()
        else:
            logger.error(f"can't refresh_remote_token: {data}\n Create a new one")
            self.remote_token_last_update = datetime.now()
            otp_code = self.getOtpCode()
            res = self.get_remote_access_token(otp_code)
        self.mqtt_client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", self.remote_access_token)
        return res


    def on_mqtt_connect(self, client, userdata, rc, a):
        try:
            logger.info("Connected with result code " + str(rc))
            topics = [MQTT_RESP_TOPIC + self.customer_id + "/#"]
            for vin in self.getVIN():
                topics.append(MQTT_EVENT_TOPIC + vin)
            for topic in topics:
                client.subscribe(topic)
                logger.info("subscribe to " + topic)
        except:
            logger.error(traceback.format_exc())

    def on_mqtt_disconnect(self, client, userdata, rc):
        try:
            logger.warn("Disconnected with result code " + str(rc))
            if rc == 1:
                self.refresh_remote_token(force=True)
            else:
                logger.warn(mqtt.error_string(rc))
        except:
            logger.error(traceback.format_exc())

    def on_mqtt_message(self, client, userdata, msg):
        charge_not_detected = False
        try:
            logger.info(f"mqtt msg {msg.topic} {str(msg.payload)}")
            data = json.loads(msg.payload)
            if msg.topic.startswith(MQTT_RESP_TOPIC):
                if "return_code" in data:
                    if data["return_code"] == "0":
                        pass
                    elif data["return_code"] == "400":
                        self.refresh_remote_token(force=True)
                        logger.error("retry last request, token was expired")
                    elif data["return_code"] == "300":
                        logger.error(f'{data["return_code"]}')
                    else:
                        logger.error(f'{data["return_code"]} : {data["reason"]}')
                else:
                    logger.debug("mqtt msg hasn't return code")
            if msg.topic.startswith(MQTT_EVENT_TOPIC):
                if data["charging_state"]['remaining_time'] != 0 and data["charging_state"]['rate'] == 0:
                    charge_not_detected = True
            elif msg.topic.endswith("/VehicleState"):
                if data["resp_data"]["charging_state"]['remaining_time'] != 0 \
                        and data["resp_data"]["charging_state"]['rate'] == 0:
                    charge_not_detected = True
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
            self.get_state(list(self.vehicles_list.keys())[0])
        except:
            logger.warn("keep_mqtt error")
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
        hour = re.findall(reg, hour_str)[0]
        h = int(hour[0])
        if hour[1] == '':
            m = 0
        else:
            m = hour[1]
        return h, m

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
        logger.info("ask wakeup to " + vin)
        msg = self.mqtt_request(vin, {"action": "state"})
        logger.info(msg)
        self.mqtt_client.publish(MQTT_REQ_TOPIC + self.customer_id + "/VehCharge/state", msg)
        return True

    #get state from server by mqtt
    def get_state(self, vin):
        logger.info("ask state to " + vin)
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
        msg = self.mqtt_request(vin, {"asap": value, "programs": {
            "program1": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
            "program2": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
            "program3": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
            "program4": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0}}})
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
            str = f.read()
            return MyPSACC(**json.loads(str))

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
        logger.debug(f"vin:{vin} longitude:{longitude} latitude:{latitude} date:{date} mileage:{mileage} level:{level} charging_status:{charging_status} charge_date:{charge_date} level_fuel:{level_fuel} moving:{moving}")
        conn = get_db()
        if mileage == 0:  # fix a bug of the api
            logger.error(f"The api return a wrong mileage for {vin} : {mileage}")
        else:
            if conn.execute("SELECT Timestamp from position where Timestamp=?", (date,)).fetchone() is None:
                temp = None
                if self.weather_api is not None:
                    try:
                        weather_rep = requests.get("https://api.openweathermap.org/data/2.5/onecall",
                                                   params={"lat": latitude, "lon": longitude,
                                                           "exclude": "minutely,hourly,daily,alerts",
                                                           "appid": "f8ee4124ea074950b696fd3e956a7069", "units": "metric"})
                        temp = weather_rep.json()["current"]["temp"]
                        logger.debug(f"Temperature :{temp}c")
                    except Exception as e:
                        logger.error(f"Unable to get temperature from openweathermap :{e}")

                if level_fuel == 0: # fix fuel level not provided when car is off
                    try:
                        level_fuel = conn.execute("SELECT level_fuel FROM position WHERE level_fuel>0 AND VIN=? ORDER BY Timestamp DESC LIMIT 1",(vin,)).fetchone()[0]
                        logger.info(f"level_fuel fixed with last real value {level_fuel} for {vin}")
                    except TypeError:
                        level_fuel = None
                        logger.info(f"level_fuel unfixed for {vin}")

                conn.execute(
                    "INSERT INTO position(Timestamp,VIN,longitude,latitude,mileage,level,level_fuel,moving,temperature) VALUES(?,?,?,?,?,?,?,?,?)",
                    (date, vin, longitude, latitude, mileage, level, level_fuel, moving, temp))

                conn.commit()
                logger.info(f"new position recorded for {vin}")
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
                    kw = (level - start_level) / 100 * ENERGY_CAPACITY[self.vehicles_list[vin]['label']]['BATTERY_POWER']
                    res = conn.execute(
                        "UPDATE battery set stop_at=?, end_level=?, co2=?, kw=? WHERE start_at=? and VIN=?",
                        (charge_date, level, co2_per_kw, kw, start_at, vin))
                    conn.commit()
            except TypeError:
                logger.debug("battery table is empty")
            except:
                logger.debug("Error when saving status " + traceback.format_exc())
        conn.close()

    @staticmethod
    def get_recorded_position():
        from geojson import Feature, Point, FeatureCollection
        from geojson import dumps as geo_dumps
        conn = get_db()
        res = conn.execute('SELECT * FROM position ORDER BY Timestamp')
        features_list = []
        for row in res:
            feature = Feature(geometry=Point((row["longitude"], row["latitude"])),
                              properties={"vin": row["vin"], "date": row["Timestamp"].strftime("%x %X"), "mileage": row["mileage"],
                                          "level": row["level"],"level_fuel": row["level_fuel"]})
            features_list.append(feature)
        feature_collection = FeatureCollection(features_list)
        conn.close()
        return geo_dumps(feature_collection, sort_keys=True)

    @staticmethod
    def get_trips(vehicle_model='208') -> List[Trip]:   # to be verified by an e208 owner - to be changed in ENERGY_CAPACITY and in get_trip function vehicle_model default value
                                                        # we should add vin parameter
                                                        # we should think moving this method in Trip.py
        conn = get_db()
        res = conn.execute('SELECT * FROM position ORDER BY Timestamp').fetchall()
        trips = []
        if len(res) > 1:
            start = res[0]
            end = res[1]
            tr = Trip()
            #res = list(map(dict,res))
            for x in range(0, len(res) - 2):
                logger.debug(f"{res[x]['Timestamp']} mileage:{res[x]['mileage']} level:{res[x]['level']} level_fuel:{res[x]['level_fuel']}")
                next_el = res[x + 2]
                distance = end["mileage"] - start["mileage"]
                duration = (end["Timestamp"] - start["Timestamp"]).total_seconds() / 3600
                try:
                    speed_average = distance / duration
                except ZeroDivisionError:
                    speed_average = 0
                charge = end["level"] - start["level"]
                if end["level_fuel"] != None and start["level_fuel"] != None:
                    refuel = end["level_fuel"] - start["level_fuel"]
                else:
                    refuel = 0
                restart_trip = False
                if refuel > 0:
                    restart_trip = True
                    logger.debug(f"refuel detected")
                elif distance == 0 and charge > 2:
                    restart_trip = True
                    logger.debug(f"charge detected")
                elif speed_average < 0.2 and duration > 0.05:   # think again if duration is really needed
                     #end["mileage"] - start["mileage"] == 0 #or \
                     #(end["Timestamp"] - start["Timestamp"]).total_seconds() / 3600 > 10:  # condition useless ???
                    restart_trip = True
                    logger.debug(f"low speed detected")
                if restart_trip:
                    start = end
                    tr = Trip()
                    logger.debug(f"restart trip at {start['Timestamp']} {start['mileage']}km level:{start['level']} level_fuel:{start['level_fuel']}")
                else:
                    distance = next_el["mileage"] - end["mileage"]  # km
                    duration = (next_el["Timestamp"] - end["Timestamp"]).total_seconds() / 3600
                    try:
                        speed_average = distance / duration
                    except ZeroDivisionError:
                        speed_average = 0
                    charge = next_el["level"] - end["level"]
                    if next_el["level_fuel"] != None and end["level_fuel"] != None:
                        refuel = next_el["level_fuel"] - end["level_fuel"]
                    else:
                        refuel = 0
                    end_trip = False
                    if refuel > 0:
                        end_trip = True
                        logger.debug(f"refuel detected")
                    elif distance == 0 and charge > 2:
                        end_trip = True
                        logger.debug(f"charge detected {charge}")
                    elif speed_average < 0.2 and duration > 0.05:
                         #(distance == 0 and duration > 0.08) or duration > 2 or  # check the speed to handle missing point
                        end_trip = True
                        logger.debug(f"low speed detected")
                    elif duration > 2:
                        end_trip = True
                        logger.debug(f"too much time detected")
                    elif x == len(res)-3:  # last record detected
                        # think if add point is needed
                        end = next_el
                        end_trip = True
                        logger.debug(f"last position found")
                    if end_trip:
                        logger.debug(f"stop trip at {end['Timestamp']} {end['mileage']}km level:{end['level']} level_fuel:{end['level_fuel']}")
                        tr.distance = end["mileage"] - start["mileage"]  # km
                        if tr.distance > 0:
                            tr.start_at = start["Timestamp"]
                            tr.end_at = end["Timestamp"]
                            tr.add_points(end["longitude"], end["latitude"])
                            tr.duration = (end["Timestamp"] - start["Timestamp"]).total_seconds() / 3600
                            tr.speed_average = tr.distance / tr.duration
                            diff_level = start["level"] - end["level"]
                            tr.consumption = diff_level / 100 * ENERGY_CAPACITY[vehicle_model]['BATTERY_POWER']  # kw
                            tr.consumption_km = 100 * tr.consumption / tr.distance  # kw/100 km
                            if start["level_fuel"] != None and end["level_fuel"] != None:
                                diff_level_fuel = start["level_fuel"] - end["level_fuel"]
                                tr.consumption_fuel = round(diff_level_fuel / 100 * ENERGY_CAPACITY[vehicle_model]['FUEL_CAPACITY'],2) # L
                                tr.consumption_fuel_km = round(100 * tr.consumption_fuel / tr.distance,2)  # L/100 km
                            tr.mileage = end["mileage"]
                            logger.debug(
                                    f"Trip: {tr.start_at} -> {tr.end_at} {tr.distance:.1f}km {tr.duration:.2f}h {tr.speed_average:.0f}km/h "
                                    f"{tr.consumption:.2f}kWh {tr.consumption_km:.2f}kWh/100km {tr.consumption_fuel}L {tr.consumption_fuel_km}L/100km "
                                    f"{tr.mileage:.1f}km")
                            # filter bad value
                            if tr.consumption_km < 70 and (tr.consumption_fuel_km == None or tr.consumption_fuel_km < 30):
                                trips.append(tr)
                            else:
                                logger.debug(f"trip discarded")
                        start = next_el
                        tr = Trip()
                    else:
                        tr.add_points(end["longitude"], end["latitude"])
                end = next_el
        return trips

    @staticmethod
    def get_chargings(min=None, max=None):
        conn = get_db()
        if min is not None:
            if max is not None:
                res = conn.execute("select * from battery WHERE start_at>=? and start_at<=?", (min, max)).fetchall()
            else:
                res = conn.execute("select * from battery WHERE start_at>=?", (min,)).fetchall()
        elif max is not None:
            res = conn.execute("select * from battery WHERE start_at<=?", (max,)).fetchall()
        else:
            res = conn.execute("select * from battery").fetchall()
        return tuple(map(dict, res))


class MyPeugeotEncoder(JSONEncoder):
    def default(self, mp: MyPSACC):
        data = copy(mp.__dict__)
        mpd = {}
        mpd["proxies"] = data["_proxies"]
        mpd["refresh_token"] = mp.manager.refresh_token
        mpd["client_secret"] = mp.service_information.client_secret
        for el in ["client_id", "realm", "remote_refresh_token", "customer_id","weather_api"]:
            mpd[el] = data[el]
        return mpd


#add method to class Energy
def get_energy(self,energy_type):
    for energy in self._energy:
        if energy.type == energy_type:
            return energy
    return psac.models.energy.Energy(charging=psac.models.energy_charging.EnergyCharging())

psac.models.status.Status.get_energy = get_energy
