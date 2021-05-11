import sys
import sqlite3
from datetime import datetime
from time import sleep

from typing import Callable
import pytz
import requests

from geojson import Feature, Point, FeatureCollection
from geojson import dumps as geo_dumps

from mylogger import logger
from libs.utils import get_temp

NEW_BATTERY_COLUMNS = [["price", "INTEGER"], ["charging_mode", "TEXT"]]
NEW_POSITION_COLUMNS = [["level_fuel", "INTEGER"], ["altitude", "INTEGER"]]


def convert_sql_res(rows):
    return list(map(dict, rows))


DATE_FORMAT = "%Y-%m-%d %H:%M:%S+00:00"


def new_convert_datetime_from_string(string):
    return datetime.fromisoformat(string)


class CustomSqliteConnection(sqlite3.Connection):

    def __init__(self, *args, **kwargs):  # real signature unknown
        super().__init__(*args, **kwargs)
        self.callbacks = []

    def execute_callbacks(self):
        for callback in self.callbacks:
            callback()

    def close(self):
        if self.total_changes:
            self.execute_callbacks()
        super().close()

class Database:
    callback_fct: Callable[[], None] = lambda: None
    DEFAULT_DB_FILE = 'info.db'
    db_initialized = False

    @staticmethod
    def convert_datetime_from_string(string):
        try:
            return datetime.strptime(string, DATE_FORMAT).replace(tzinfo=pytz.UTC)
        except ValueError:
            return datetime.strptime(string.replace("T", " "), DATE_FORMAT).replace(tzinfo=pytz.UTC)

    @staticmethod
    def convert_datetime_from_bytes(bytes_string):
        return Database.convert_datetime_from_string(bytes_string.decode("utf-8"))

    @staticmethod
    def convert_datetime_to_string(date: datetime):
        return date.replace(tzinfo=pytz.UTC).isoformat(timespec='seconds', sep=" ")

    @staticmethod
    def set_db_callback(callbackfct):
        Database.callback_fct = callbackfct

    @staticmethod
    def backup(conn):
        if sys.version_info < (3, 7):
            logger.warning("Can't do database backup, please upgrade to python 3.7")
        else:
            back_conn = sqlite3.connect("info_backup.db")
            conn.backup(back_conn)
            back_conn.close()

    @staticmethod
    def init_db(conn):
        conn.execute("""CREATE TABLE IF NOT EXISTS position (Timestamp DATETIME PRIMARY KEY,
                                                             VIN TEXT, longitude REAL,
                                                             latitude REAL,
                                                             mileage REAL,
                                                             level INTEGER,
                                                             level_fuel INTEGER,
                                                             moving BOOLEAN,
                                                             temperature INTEGER,
                                                             altitude INTEGER);""")
        make_backup = False
        conn.execute("CREATE TABLE IF NOT EXISTS battery (start_at DATETIME PRIMARY KEY,stop_at DATETIME,VIN TEXT, "
                     "start_level INTEGER, end_level INTEGER, co2 INTEGER, kw INTEGER);")
        conn.execute("""CREATE TABLE IF NOT EXISTS battery_curve (start_at DATETIME, VIN TEXT, date DATETIME,
                        level INTEGER, UNIQUE(start_at, VIN, level));""")
        for table, columns in [["position", NEW_POSITION_COLUMNS], ["battery", NEW_BATTERY_COLUMNS]]:
            for column, column_type in columns:
                try:
                    conn.execute(f"ALTER TABLE {table} ADD {column} {column_type};")
                    make_backup = True
                except sqlite3.OperationalError:
                    pass
        if make_backup:
            Database.backup(conn)
        Database.clean_battery(conn)
        Database.add_altitude_to_db(conn)
        conn.commit()
        if sys.version_info >= (3, 7):
            Database.convert_datetime_from_string = new_convert_datetime_from_string
        sqlite3.register_converter("DATETIME", Database.convert_datetime_from_bytes)
        sqlite3.register_adapter(datetime, Database.convert_datetime_to_string)
        Database.db_initialized = True

    @staticmethod
    def get_db(db_file=None, update_callback=True) -> CustomSqliteConnection:
        if db_file is None:
            db_file = Database.DEFAULT_DB_FILE
        conn = CustomSqliteConnection(db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        if not Database.db_initialized:
            Database.init_db(conn)
        if update_callback:
            conn.callbacks.append(Database.callback_fct)
        return conn

    @staticmethod
    def clean_battery(conn):
        # delete charging longer than 17h
        conn.execute("DElETE FROM battery WHERE JULIANDAY(stop_at)-JULIANDAY(start_at)>0.7;")
        # delete charging not finished longer than 17h
        conn.execute("DELETE from battery where stop_at is NULL and JULIANDAY()-JULIANDAY(start_at)>0.7;")
        #delete little charge
        conn.execute("DELETE FROM battery WHERE start_level >= end_level-1;")

    @staticmethod
    def clean_position(conn):
        res = conn.execute(
            "SELECT Timestamp,mileage,level from position ORDER BY Timestamp DESC LIMIT 3;").fetchall()
        # Clean DB
        if len(res) == 3 and res[0]["mileage"] == res[1]["mileage"] == res[2]["mileage"] and \
                res[0]["level"] == res[1]["level"] == res[2]["level"]:
            logger.debug("Delete duplicate line")
            conn.execute("DELETE FROM position where Timestamp=?;", (res[1]["Timestamp"],))
            conn.commit()

    @staticmethod
    def get_last_temp(vin):
        conn = Database.get_db()
        res = conn.execute("SELECT temperature FROM position WHERE VIN=? ORDER BY Timestamp DESC limit 1",
                           (vin,)).fetchone()
        conn.close()
        if res is None:
            return None
        return res[0]

    @staticmethod
    def set_chargings_price(conn, start_at, price):
        if isinstance(start_at, str):
            start_at = Database.convert_datetime_from_string(start_at)
        update = conn.execute("UPDATE battery SET price=? WHERE start_at=?", (price, start_at)).rowcount == 1
        conn.commit()
        if not update:
            logger.error("Can't find line to update in the database")
        return update

    @staticmethod
    def get_battery_curve(conn, start_at, vin):
        return convert_sql_res(conn.execute("""SELECT date, level FROM battery_curve
                                                WHERE start_at=? and VIN=?;""", (start_at, vin)).fetchall())

    @staticmethod
    def add_altitude_to_db(conn):
        max_pos_by_req = 100
        nb_null = conn.execute(
            "SELECT COUNT(1) FROM position WHERE altitude IS NULL;").fetchone()[0]
        if nb_null > max_pos_by_req:
            logger.warning("There is %s to fetch from API, it can take some time", nb_null)
        try:
            while True:
                res = conn.execute("SELECT DISTINCT latitude,longitude "
                                   "FROM position WHERE altitude IS NULL LIMIT ?;", (max_pos_by_req,)).fetchall()
                nb_res = len(res)
                if nb_res > 0:
                    logger.debug("add altitude for %s positions point", nb_null)
                    nb_null -= nb_res
                    locations_str = ""
                    for line in res:
                        locations_str += str(line[0]) + "," + str(line[1]) + "|"
                    locations_str = locations_str[:-1]
                    res = requests.get("https://api.opentopodata.org/v1/srtm30m",
                                       params={"locations": locations_str})
                    data = res.json()["results"]
                    for line in data:
                        conn.execute("UPDATE position SET altitude=? WHERE latitude=? and longitude=?",
                                     (line["elevation"], line["location"]["lat"], line["location"]["lng"]))
                    conn.commit()
                    if nb_res == 100:
                        sleep(1)  # API is limited to 1 call by sec
                else:
                    break
        except (ValueError, KeyError, requests.exceptions.RequestException):
            logger.error("Can't get altitude from API")

    @staticmethod
    def get_recorded_position():
        conn = Database.get_db()
        res = conn.execute('SELECT * FROM position ORDER BY Timestamp')
        features_list = []
        for row in res:
            if row["longitude"] is None or row["latitude"] is None:
                continue
            feature = Feature(geometry=Point((row["longitude"], row["latitude"])),
                              properties={"vin": row["vin"], "date": row["Timestamp"].strftime("%x %X"),
                                          "mileage": row["mileage"],
                                          "level": row["level"], "level_fuel": row["level_fuel"]})
            features_list.append(feature)
        feature_collection = FeatureCollection(features_list)
        conn.close()
        return geo_dumps(feature_collection, sort_keys=True)

    # pylint: disable=too-many-arguments
    @staticmethod
    def record_position(weather_api, vin, mileage, latitude, longitude, altitude, date, level, level_fuel, moving):
        if mileage == 0:  # fix a bug of the api
            logger.error("The api return a wrong mileage for %s : %f", vin, mileage)
        else:
            conn = Database.get_db()
            if conn.execute("SELECT Timestamp from position where Timestamp=?", (date,)).fetchone() is None:
                temp = get_temp(latitude, longitude, weather_api)
                if level_fuel == 0:  # fix fuel level not provided when car is off
                    try:
                        level_fuel = conn.execute(
                            "SELECT level_fuel FROM position WHERE level_fuel>0 AND VIN=? ORDER BY Timestamp DESC "
                            "LIMIT 1",
                            (vin,)).fetchone()[0]
                        logger.info("level_fuel fixed with last real value %f for %s", level_fuel, vin)
                    except TypeError:
                        level_fuel = None
                        logger.info("level_fuel unfixed for %s", vin)

                conn.execute("INSERT INTO position(Timestamp,VIN,longitude,latitude,altitude,mileage,level,level_fuel,"
                             "moving,temperature) VALUES(?,?,?,?,?,?,?,?,?,?)",
                             (date, vin, longitude, latitude, altitude, mileage, level, level_fuel, moving, temp))

                conn.commit()
                logger.info("new position recorded for %s", vin)
                Database.clean_position(conn)
                conn.close()
                return True
            conn.close()
            logger.debug("position already saved")
        return False
