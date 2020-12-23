import sqlite3
from datetime import datetime
import pytz


def convert_datetime(st):
    return datetime.strptime(st.decode("utf-8"), "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=pytz.UTC)


sqlite3.register_converter("DATETIME", convert_datetime)
conn = sqlite3.connect('info.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
conn.execute("CREATE TABLE IF NOT EXISTS position (Timestamp DATETIME PRIMARY KEY, VIN TEXT, longitude REAL, "
             "latitude REAL, mileage REAL, level INTEGER);")
conn.commit()


