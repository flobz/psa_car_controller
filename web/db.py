import sqlite3
from datetime import datetime

import pytz
from typing import Callable

from MyLogger import logger

callback_fct: Callable[[], None] = lambda: None
default_db_file = 'info.db'
db_initialized = False


def convert_datetime_from_bytes(bytes_string):
    return datetime.strptime(bytes_string.decode("utf-8"), "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=pytz.UTC)


def convert_datetime_from_string(st):
    return datetime.strptime(st, "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=pytz.UTC)


def update_callback():
    callback_fct()


def set_db_callback(callbackfct):
    global callback_fct
    callback_fct = callbackfct


def backup(conn):
    back_conn = sqlite3.connect("info_backup.db")
    conn.backup(back_conn)
    back_conn.close()


def init_db(conn):
    global db_initialized
    conn.execute("CREATE TABLE IF NOT EXISTS position (Timestamp DATETIME PRIMARY KEY, VIN TEXT, longitude REAL, "
                 "latitude REAL, mileage REAL, level INTEGER, level_fuel INTEGER, moving BOOLEAN, temperature INTEGER);")
    make_backup = False
    try:
        conn.execute("ALTER TABLE position ADD level_fuel INTEGER;")
        make_backup = True
    except sqlite3.OperationalError:
        pass
    conn.execute("CREATE TABLE IF NOT EXISTS battery (start_at DATETIME PRIMARY KEY,stop_at DATETIME,VIN TEXT, "
                 "start_level INTEGER, end_level INTEGER, co2 INTEGER, kw INTEGER);")
    conn.create_function("update_trips", 0, update_callback)
    conn.execute("CREATE TEMP TRIGGER IF NOT EXISTS update_trigger AFTER INSERT ON position BEGIN "
                 "SELECT update_trips(); END;")
    try:
        conn.execute("ALTER TABLE battery ADD price INTEGER;")
        make_backup = True
    except sqlite3.OperationalError:
        pass
    if make_backup:
        backup(conn)
    clean_battery(conn)
    conn.commit()
    db_initialized = True


def get_db(db_file=default_db_file):
    sqlite3.register_converter("DATETIME", convert_datetime_from_bytes)
    conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    if not db_initialized:
        init_db(conn)
    return conn


def clean_battery(conn):
    # delete charging longer than 17h
    conn.execute("DElETE FROM battery WHERE JULIANDAY(stop_at)-JULIANDAY(start_at)>0.7;")
    conn.execute("DELETE FROM battery WHERE start_level==end_level;")
    conn.commit()


def clean_position(conn):
    res = conn.execute(
        "SELECT Timestamp,mileage,level from position ORDER BY Timestamp DESC LIMIT 3;").fetchall()
    # Clean DB
    if len(res) == 3 and res[0]["mileage"] == res[1]["mileage"] == res[2]["mileage"] and \
            res[0]["level"] == res[1]["level"] == res[2]["level"]:
        logger.debug("Delete duplicate line")
        conn.execute("DELETE FROM position where Timestamp=?;", (res[1]["Timestamp"],))
        conn.commit()


def get_last_temp(vin):
    conn = get_db()
    res = conn.execute("SELECT temperature FROM position WHERE VIN=? ORDER BY Timestamp DESC limit 1",
                       (vin,)).fetchone()
    if res is None:
        return None
    return res[0]


def set_chargings_price(conn, start_at, price):
    if isinstance(start_at, str):
        start_at = convert_datetime_from_string(start_at)
    update = conn.execute("UPDATE battery SET price=? WHERE start_at=?", (price, start_at)).rowcount == 1
    conn.commit()
    if not update:
        logger.error("Can't find line to update in the database")
    return update