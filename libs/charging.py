from datetime import datetime
from sqlite3 import IntegrityError

from typing import List

from ecomix import Ecomix
from libs.elec_price import ElecPrice
from mylogger import logger
from web.db import Database


class Charging:
    elec_price: ElecPrice = ElecPrice(None)

    @staticmethod
    def get_chargings() -> List[dict]:
        conn = Database.get_db()
        res = conn.execute("select * from battery ORDER BY start_at").fetchall()
        conn.close()
        return list(map(dict, res))

    @staticmethod
    def set_default_price():
        if Charging.elec_price.is_enable():
            conn = Database.get_db()
            charge_list = list(map(dict, conn.execute("SELECT * FROM battery WHERE price IS NULL").fetchall()))
            for charge in charge_list:
                charge["price"] = Charging.elec_price.get_price(charge["start_at"], charge["stop_at"], charge["kw"])
                Database.set_chargings_price(conn, charge["start_at"], charge["price"])
            conn.close()

    # pylint: disable=too-many-arguments
    @staticmethod
    def update_chargings(conn, start_at, stop_at, level, co2_per_kw, consumption_kw, vin):
        price = Charging.elec_price.get_price(start_at, stop_at, consumption_kw)
        conn.execute(
            "UPDATE battery set stop_at=?, end_level=?, co2=?, kw=?, price=? WHERE start_at=? and VIN=?",
            (stop_at, level, co2_per_kw, consumption_kw, price, start_at, vin))
        Database.clean_battery(conn)

    @staticmethod
    def record_charging(car, charging_status, charge_date: datetime, level, latitude, # pylint: disable=too-many-locals
                        longitude, country_code, charging_mode, charging_rate, autonomy):
        conn = Database.get_db()
        charge_date = charge_date.replace(microsecond=0)
        if charging_status == "InProgress":
            stop_at, start_at = conn.execute("SELECT stop_at, start_at FROM battery WHERE VIN=? ORDER BY start_at "
                               "DESC limit 1", (car.vin,)).fetchone() or [False, None]
            try:
                conn.execute("INSERT INTO battery_curve(start_at,VIN,date,level,rate,autonomy) VALUES(?,?,?,?,?,?)",
                             (start_at, car.vin, charge_date, level, charging_rate, autonomy))
            except IntegrityError:
                logger.debug("level already stored")
            if stop_at is not None:
                conn.execute("INSERT INTO battery(start_at,start_level,charging_mode,VIN) VALUES(?,?,?,?)",
                             (charge_date, level, charging_mode, car.vin))
            Ecomix.get_data_from_co2_signal(latitude, longitude, country_code)
        else:
            try:
                start_at, stop_at, start_level = conn.execute(
                    "SELECT start_at, stop_at, start_level from battery WHERE VIN=? ORDER BY start_at DESC limit 1",
                    (car.vin,)).fetchone()
                in_progress = stop_at is None
            except TypeError:
                logger.debug("battery table is probably empty :", exc_info=True)
                in_progress = False
            if in_progress:
                co2_per_kw = Ecomix.get_co2_per_kw(start_at, charge_date, latitude, longitude, country_code)
                consumption_kw = (level - start_level) / 100 * car.battery_power
                Charging.update_chargings(conn, start_at, charge_date, level, co2_per_kw, consumption_kw, car.vin)
        conn.commit()
        conn.close()
