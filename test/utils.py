# flake8: noqa

import os
from datetime import timedelta, datetime

import pytz

from libs.car import Car, Cars
from libs.charging import Charging
from web.db import Database

DATA_DIR = os.path.dirname(os.path.realpath(__file__)) + "/data/"
latitude = 47.2183
longitude = -1.55362
date3 = datetime.utcnow().replace(2021, 3, 1, 12, 00, 00, 00, tzinfo=pytz.UTC)
date2 = date3 - timedelta(minutes=20)
date1 = date3 - timedelta(minutes=40)
date0 = date3 - timedelta(minutes=60)
date4 = date3 + timedelta(minutes=1)

vehicule_list = Cars()
vehicule_list.extend(
    [Car("VR3UHZKX", "vid", "Peugeot"), Car("VXXXXX", "XXXX", "Peugeot", label="SUV 3008 Hybrid 225")])
car = vehicule_list[0]
DB_DIR = DATA_DIR + "tmp.db"


def get_new_test_db():
    try:
        os.remove(DATA_DIR + "tmp.db")
    except FileNotFoundError:
        pass
    Database.DEFAULT_DB_FILE = DB_DIR
    Database.db_initialized = False
    conn = Database.get_db()
    return conn


def record_position():
    Database.record_position(None, car.vin, 11, latitude, longitude - 0.05, None, date0, 40, None, False)
    Database.record_position(None, car.vin, 20, latitude, longitude, 32, date1, 35, None, False)
    Database.record_position(None, car.vin, 30, latitude, longitude, 42, date2, 30, None, False)


def record_charging():
    Charging.record_charging(car, "InProgress", date0, 50, latitude, longitude, "FR", "slow", 20, 60)
    Charging.record_charging(car, "InProgress", date1, 75, latitude, longitude, "FR", "slow", 20, 60)
    Charging.record_charging(car, "InProgress", date2, 85, latitude, longitude, "FR", "slow", 20, 60)
    Charging.record_charging(car, "InProgress", date3, 90, latitude, longitude, "FR", "slow", 20, 60)
    Charging.record_charging(car, "Stopped", date4, 91, latitude, longitude, "FR", "slow", 20, 60)


def get_date(offset):
    return date3 + timedelta(minutes=60 * offset)
