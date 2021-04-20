from libs.elec_price import ElecPrice
from web.db import get_db, set_chargings_price, clean_battery

elec_price = ElecPrice.read_config()


class Charging:
    @staticmethod
    def get_chargings(mini=None, maxi=None) -> list[dict]:
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
            for el in charge_list:
                el["price"] = elec_price.get_price(el["start_at"], el["stop_at"], el["kw"])
                set_chargings_price(conn, el["start_at"], el["price"])
            conn.close()

    @staticmethod
    def update_chargings(conn, start_at, stop_at, level, co2_per_kw, kw, vin):
        price = elec_price.get_price(start_at, stop_at, kw)
        conn.execute(
            "UPDATE battery set stop_at=?, end_level=?, co2=?, kw=?, price=? WHERE start_at=? and VIN=?",
            (stop_at, level, co2_per_kw, kw, price, start_at, vin))
        clean_battery(conn)
