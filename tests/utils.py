# flake8: noqa

import os
from datetime import timedelta, datetime
from unittest.mock import MagicMock

import pytz
from deepdiff import DeepDiff

from psa_car_controller.psa.RemoteClient import RemoteClient
from psa_car_controller.psa.connected_car_api import Vehicles
from psa_car_controller.psacc.application.charging import Charging
from psa_car_controller.psacc.model.car import Cars, Car
from psa_car_controller.psacc.repository.db import Database

DATA_DIR = os.path.dirname(os.path.realpath(__file__)) + "/data/"
latitude = 47.2183
longitude = -1.55362
date3 = datetime.utcnow().replace(2021, 3, 1, 12, 00, 00, 00, tzinfo=pytz.UTC)
date2 = date3 - timedelta(minutes=20)
date1 = date3 - timedelta(minutes=40)
date0 = date3 - timedelta(minutes=60)
date4 = date3 + timedelta(minutes=1)
duration_min = (date3 - date0).seconds / 60
duration_str = str(date3 - date0)

vehicule_list = Cars()
vehicule_list.extend(
    [Car("VR3UHZKX", "vid", "Peugeot"), Car("VXXXXX", "XXXX", "Peugeot", label="SUV 3008 Hybrid 225")])
car = vehicule_list[0]


def get_new_test_db():
    Database.close_db()
    conn = Database.get_db(force_new_conn=True, db_file="")
    return conn


def record_position():
    Database.record_position(None, car.vin, 11, latitude, longitude - 0.05, None, date0, 40, None, False, None)
    Database.record_position(None, car.vin, 20, latitude, longitude, 32, date1, 35, None, False, None)
    Database.record_position(None, car.vin, 30, latitude, longitude, 42, date2, 30, None, False, None)
    Database.record_position(None, car.vin, None, latitude, longitude, 42, date2, 30, None, False, None)


def record_charging():
    Charging.record_charging(car, "InProgress", date0, 50, latitude, longitude, "FR", "slow", 20, 60, 123456789.1)
    Charging.record_charging(car, "InProgress", date1, 75, latitude, longitude, "FR", "slow", 20, 60, 123456789.1)
    Charging.record_charging(car, "InProgress", date2, 85, latitude, longitude, "FR", "slow", 20, 60, 123456789.1)
    Charging.record_charging(car, "InProgress", date3, 90, latitude, longitude, "FR", "slow", 20, 60, 123456789.1)
    Charging.record_charging(car, "Stopped", date4, 91, latitude, longitude, "FR", "slow", 20, 60, 123456789.1)


def get_date(offset):
    return date3 + timedelta(minutes=60 * offset)


def get_rc() -> RemoteClient:
    account_info = MagicMock()
    account_info.realm = ""
    return RemoteClient(account_info, Vehicles, None, None)


def compare_dict(result, expected):
    diff = DeepDiff(expected, result)
    if diff != {}:
        raise AssertionError(str(diff))
    return True
