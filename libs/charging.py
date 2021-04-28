from typing import List

from libs.elec_price import ElecPrice
from web.db import get_db, set_chargings_price, clean_battery

elec_price = ElecPrice.read_config()


class Charging:
    @staticmethod
    def get_chargings(mini=None, maxi=None) -> List[dict]:
        conn = get_db()
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
        if elec_price.is_enable():
            conn = get_db()
            charge_list = list(map(dict, conn.execute("SELECT * FROM battery WHERE price IS NULL").fetchall()))
            for charge in charge_list:
                charge["price"] = elec_price.get_price(charge["start_at"], charge["stop_at"], charge["kw"])
                set_chargings_price(conn, charge["start_at"], charge["price"])
            conn.close()

    # pylint: disable=too-many-arguments
    @staticmethod
    def update_chargings(conn, start_at, stop_at, level, co2_per_kw, consumption_kw, vin):
        price = elec_price.get_price(start_at, stop_at, consumption_kw)
        conn.execute(
            "UPDATE battery set stop_at=?, end_level=?, co2=?, kw=?, price=? WHERE start_at=? and VIN=?",
            (stop_at, level, co2_per_kw, consumption_kw, price, start_at, vin))
        clean_battery(conn)
