import logging
from datetime import datetime
from sqlite3 import IntegrityError

from typing import List

from .battery_charge_curve import BatteryChargeCurve
from .ecomix import Ecomix

from psa_car_controller.psacc.repository.config_repository import ElectricityPriceConfig
from psa_car_controller.psacc.repository.db import Database
from ..model.car import Car, Cars
from ..model.charge import Charge

logger = logging.getLogger(__name__)


class Charging:
    elec_price: ElectricityPriceConfig = ElectricityPriceConfig()

    @staticmethod
    def get_chargings() -> List[dict]:
        charge_db = Database.get_all_charge()
        charge_list = list(map(dict, charge_db))
        Charging._calculated_fields(charge_list)
        return charge_list

    @staticmethod
    def get_battery_curve(conn, charge, car) -> List[BatteryChargeCurve]:
        battery_curves_dto = Database.get_battery_curve(conn, charge.start_at, charge.stop_at, charge.vin)
        battery_curves = BatteryChargeCurve.dto_to_battery_curve(car, charge, battery_curves_dto)
        return battery_curves

    @staticmethod
    def set_charge_price(charge, conn, car):
        battery_curves = Charging.get_battery_curve(conn, charge, car)
        charge.price = Charging.elec_price.get_price(charge, battery_curves)

    @staticmethod
    def set_default_price(cars: Cars):
        if Charging.elec_price.is_enable():
            conn = Database.get_db()
            charge_list = Database.get_all_charge_without_price(conn)
            for charge in charge_list:
                Charging.set_charge_price(charge, conn, cars.get_car_by_vin(charge.vin))
                Database.set_chargings_price(conn, charge)
            conn.close()

    # pylint: disable=too-many-arguments
    @staticmethod
    def update_chargings(conn, charge: Charge, car):
        Charging.set_charge_price(charge, conn, car)
        Database.update_charge(charge)
        Database.clean_battery(conn)

    @staticmethod
    def is_charge_ended(charge: 'Charge'):
        return not charge or charge.stop_at

    @staticmethod
    def record_charging(car: Car, charging_status, charge_date: datetime, level, latitude,
                        # pylint: disable=too-many-locals
                        longitude, country_code, charging_mode, charging_rate, autonomy, mileage):
        conn = Database.get_db()
        charge_date = charge_date.replace(microsecond=0)
        if charging_status == "InProgress":
            last_charge = Database.get_last_charge(car.vin)
            if Charging.is_charge_ended(last_charge):
                conn.execute("INSERT INTO battery(start_at,start_level,charging_mode,VIN,mileage) VALUES(?,?,?,?,?)",
                             (charge_date, level, charging_mode, car.vin, mileage))
                start_at = charge_date
            else:
                start_at = last_charge.start_at
            try:
                conn.execute(
                    "INSERT INTO battery_curve(start_at,VIN,date,level,rate,autonomy) VALUES(?,?,?,?,?,?)",
                    (start_at, car.vin, charge_date, level, charging_rate, autonomy))
            except IntegrityError:
                # todo add charging rate to unique constraint
                logger.debug("level already stored")
            Ecomix.get_data_from_co2_signal(latitude, longitude, country_code)
        else:
            try:
                last_charge = Database.get_last_charge(car.vin)
                charge_just_finished = last_charge.stop_at is None
            except (TypeError, AttributeError):
                logger.debug("battery table is probably empty :", exc_info=True)
                charge_just_finished = False
            if charge_just_finished:
                co2_per_kw = Ecomix.get_co2_per_kw(last_charge.start_at, charge_date, latitude, longitude, country_code)
                consumption_kw = (level - last_charge.start_level) / 100 * car.battery_power
                last_charge.end_level = level
                last_charge.co2 = co2_per_kw
                last_charge.kw = consumption_kw
                last_charge.stop_at = charge_date
                last_charge.mileage = mileage
                Charging.update_chargings(conn, last_charge, car)
        conn.commit()
        conn.close()

    @staticmethod
    def _calculated_fields(charge_list: list):
        for c in charge_list:
            if c.get("stop_at") and c.get("start_at"):
                c.update(
                    {
                        "duration_min": (c.get("stop_at") - c.get("start_at")).total_seconds()
                        / 60,
                        "duration_str": str((c.get("stop_at") - c.get("start_at"))),
                    }
                )