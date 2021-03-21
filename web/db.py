import sqlite3
from datetime import datetime

import pytz
from typing import Callable

from MyLogger import logger

callback_fct: Callable[[], None] = lambda: None
default_db_file = 'info.db'


def convert_datetime(st):
    return datetime.strptime(st.decode("utf-8"), "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=pytz.UTC)


def update_callback():
    callback_fct()


def get_db(db_file=default_db_file):
    sqlite3.register_converter("DATETIME", convert_datetime)
    conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS position (Timestamp DATETIME PRIMARY KEY, VIN TEXT, longitude REAL, "
                 "latitude REAL, mileage REAL, level INTEGER, level_fuel INTEGER, moving BOOLEAN, temperature INTEGER);")
    try:
        conn.execute("ALTER TABLE position ADD level_fuel INTEGER;")
    except sqlite3.OperationalError:
        pass
    conn.execute("CREATE TABLE IF NOT EXISTS battery (start_at DATETIME PRIMARY KEY,stop_at DATETIME,VIN TEXT, "
                 "start_level INTEGER, end_level INTEGER, co2 INTEGER, kw INTEGER);")
    conn.create_function("update_trips", 0, update_callback)
    conn.execute("CREATE TEMP TRIGGER IF NOT EXISTS update_trigger AFTER INSERT ON position BEGIN "
                 "SELECT update_trips(); END;")
    conn.commit()
    return conn


def clean_position(conn):
    res = conn.execute(
        "SELECT Timestamp,mileage,level from position ORDER BY Timestamp DESC LIMIT 3;").fetchall()
    # Clean DB
    if len(res) == 3 and res[0]["mileage"] == res[1]["mileage"] == res[2]["mileage"] and \
            res[0]["level"] == res[1]["level"] == res[2]["level"]:
        logger.debug("Delete duplicate line")
        conn.execute("DELETE FROM position where Timestamp=?;", (res[1]["Timestamp"],))
        conn.commit()
