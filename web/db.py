import sqlite3
from datetime import datetime
import pytz

callback_fct = None

def convert_datetime(st):
    return datetime.strptime(st.decode("utf-8"), "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=pytz.UTC)


def update_callback():
    if callback_fct is not None:
        callback_fct()
    return

def get_db():
    sqlite3.register_converter("DATETIME", convert_datetime)
    conn = sqlite3.connect('info.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS position (Timestamp DATETIME PRIMARY KEY, VIN TEXT, longitude REAL, "
                 "latitude REAL, mileage REAL, level INTEGER);")
    conn.create_function("update_trips", 0, update_callback)
    conn.execute(
        "CREATE TEMP TRIGGER IF NOT EXISTS update_trigger AFTER INSERT ON position BEGIN SELECT update_trips(); END;")
    conn.commit()
    conn.commit()
    return conn
