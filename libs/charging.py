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
    def get_chargings(mini=None, maxi=None) -> List[dict]:
        conn = Database.get_db()
        if mini is not None:
            if maxi is not None:
                res = conn.execute("select * from battery WHERE start_at>=? and start_at<=?", (mini, maxi)).fetchall()
            else:
                res = conn.execute("select * from battery WHERE start_at>=?", (mini,)).fetchall()
        elif maxi is not None:
            res = conn.execute("select * from battery WHERE start_at<=?", (maxi,)).fetchall()
        else:
            res = conn.execute("select * from battery").fetchall()
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
    def record_charging(car, charging_status, charge_date: datetime, level, latitude, longitude, country_code, charging_mode):
        conn = Database.get_db()
        charge_date = charge_date.replace(microsecond=0)
        if charging_status == "InProgress":
            res = conn.execute("SELECT stop_at, start_at FROM battery WHERE VIN=? ORDER BY start_at "
                               "DESC limit 1", (car.vin,)).fetchone()
            in_progress = res and res[0] is None
            if in_progress:
                start_at = res[1]
                try:
                    conn.execute("INSERT INTO battery_curve(start_at,VIN,date,level) VALUES(?,?,?,?)",
                                 (start_at, car.vin, charge_date, level))
                except IntegrityError:
                    logger.debug("level already stored")
            else:
                conn.execute("INSERT INTO battery(start_at,start_level,charging_mode,VIN) VALUES(?,?,?,?)",
                             (charge_date, level, charging_mode, car.vin))
            Ecomix.get_data_from_co2_signal(latitude, longitude, country_code)
        else:
            try:
                start_at, stop_at, start_level = conn.execute(
                    "SELECT start_at, stop_at, start_level from battery WHERE VIN=? ORDER BY start_at "
                    "DESC limit 1", (car.vin,)).fetchone()
                in_progress = stop_at is None
                if in_progress:
                    co2_per_kw = Ecomix.get_co2_per_kw(start_at, charge_date, latitude, longitude, country_code)
                    consumption_kw = (level - start_level) / 100 * car.battery_power

                    Charging.update_chargings(conn, start_at, charge_date, level, co2_per_kw, consumption_kw, car.vin)
            except TypeError:
                logger.debug("battery table is probably empty :", exc_info=True)
        conn.commit()
        conn.close()
