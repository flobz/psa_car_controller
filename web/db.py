import sys
import sqlite3
from datetime import datetime

from typing import Callable
import pytz

from mylogger import logger

NEW_BATTERY_COLUMNS = [["battery", "INTEGER"], ["charging_mode", "TEXT"]]

DATE_FORMAT = "%Y-%m-%d %H:%M:%S+00:00"


def convert_sql_res(rows):
    return list(map(dict, rows))


class Database:
    callback_fct: Callable[[], None] = lambda: None
    DEFAULT_DB_FILE = 'info.db'
    # pylint: disable=invalid-name
    db_initialized = False

    @staticmethod
    def convert_datetime_from_bytes(bytes_string):
        return datetime.strptime(bytes_string.decode("utf-8"), DATE_FORMAT).replace(tzinfo=pytz.UTC)


    @staticmethod
    def convert_datetime_from_string(st):
        return datetime.strptime(st, DATE_FORMAT).replace(tzinfo=pytz.UTC)

    @staticmethod
    def convert_datetime_to_string(date: datetime):
        return date.replace(tzinfo=pytz.UTC).strftime(DATE_FORMAT)

    @staticmethod
    def update_callback():
        Database.callback_fct()

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
        conn.execute("CREATE TABLE IF NOT EXISTS position (Timestamp DATETIME PRIMARY KEY, VIN TEXT, longitude REAL, "
                     "latitude REAL, mileage REAL, level INTEGER, level_fuel INTEGER, moving BOOLEAN,"
                     " temperature INTEGER);")
        make_backup = False
        try:
            conn.execute("ALTER TABLE position ADD level_fuel INTEGER;")
            make_backup = True
        except sqlite3.OperationalError:
            pass
        conn.execute("CREATE TABLE IF NOT EXISTS battery (start_at DATETIME PRIMARY KEY,stop_at DATETIME,VIN TEXT, "
                     "start_level INTEGER, end_level INTEGER, co2 INTEGER, kw INTEGER);")
        conn.create_function("update_trips", 0, Database.update_callback)
        conn.execute("CREATE TEMP TRIGGER IF NOT EXISTS update_trigger AFTER INSERT ON position BEGIN "
                     "SELECT update_trips(); END;")
        conn.execute("""CREATE TABLE IF NOT EXISTS battery_curve (start_at DATETIME, VIN TEXT, date DATETIME,
                        level INTEGER, UNIQUE(start_at, VIN, level));""")
        for column, column_type in NEW_BATTERY_COLUMNS:
            try:
                conn.execute(f"ALTER TABLE battery ADD {column} {column_type};")
                make_backup = True
            except sqlite3.OperationalError:
                pass
        if make_backup:
            Database.backup(conn)
        Database.clean_battery(conn)
        conn.commit()
        Database.db_initialized = True

    @staticmethod
    def get_db(db_file=None):
        if db_file is None:
            db_file = Database.DEFAULT_DB_FILE
        sqlite3.register_converter("DATETIME", Database.convert_datetime_from_bytes)
        sqlite3.register_adapter(datetime, Database.convert_datetime_to_string)
        conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        if not Database.db_initialized:
            Database.init_db(conn)
        return conn

    @staticmethod
    def clean_battery(conn):
        # delete charging longer than 17h
        conn.execute("DElETE FROM battery WHERE JULIANDAY(stop_at)-JULIANDAY(start_at)>0.7;")
        conn.execute("DELETE FROM battery WHERE start_level==end_level;")
        conn.commit()

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
