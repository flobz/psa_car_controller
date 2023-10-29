from statistics import mean

from typing import List

from psa_car_controller.psacc.model.battery_curve import BatteryCurveDto
from psa_car_controller.psacc.model.car import Car
from psa_car_controller.psacc.model.charge import Charge
from psa_car_controller.psacc.repository.db import Database

DEFAULT_KM_BY_KW = 5.3
MINIMUM_AUTONOMY_FOR_GOOD_RESULT = 20


class BatteryChargeCurve:
    def __init__(self, level, speed):
        self.level = level
        self.speed = speed

    @staticmethod
    def dto_to_battery_curve(car: Car, charge: Charge, battery_curves_dto: List[BatteryCurveDto]) \
            -> 'List[BatteryChargeCurve]':  # pylint: disable=too-many-locals
        start_date = charge.start_at
        stop_at = charge.stop_at
        conn = Database.get_db()
        conn.close()
        battery_curves = []
        if len(battery_curves_dto) > 0 and battery_curves_dto[-1].level > 0 and battery_curves_dto[-1].autonomy > 0:
            battery_capacity = battery_curves_dto[-1].level * car.battery_power / 100
            if battery_curves_dto[-1].autonomy > MINIMUM_AUTONOMY_FOR_GOOD_RESULT:
                km_by_kw = 0.8 * battery_curves_dto[-1].autonomy / battery_capacity
            else:
                km_by_kw = DEFAULT_KM_BY_KW
            start = 0
            speeds = []

            def speed_in_kw_from_km(battery_curve_dto):
                try:
                    speed = battery_curve_dto.rate / km_by_kw
                    if speed > 0:
                        speeds.append(speed)
                except (KeyError, TypeError):
                    pass

            for end in range(1, len(battery_curves_dto)):
                start_level = battery_curves_dto[start].level
                end_level = battery_curves_dto[end].level
                diff_level = end_level - start_level
                diff_sec = (battery_curves_dto[end].date - battery_curves_dto[start].date).total_seconds()
                speed_in_kw_from_km(battery_curves_dto[end - 1])
                if diff_sec > 0 and diff_level > 3:
                    speed_in_kw_from_km(battery_curves_dto[end])
                    speed = car.get_charge_speed(diff_level, diff_sec)
                    if len(speeds) > 0:
                        speed = mean([*speeds, speed])
                    speed = round(speed * 2) / 2
                    battery_curves.append(BatteryChargeCurve(start_level, speed))
                    start = end
                    speeds = []
            battery_curves.append(BatteryChargeCurve(charge.end_level, 0))
        elif charge.end_level and charge.start_level is not None:
            speed = car.get_charge_speed(charge.end_level - charge.start_level, (stop_at - start_date).total_seconds())
            battery_curves.append(BatteryChargeCurve(charge.start_level, speed))
            battery_curves.append(BatteryChargeCurve(charge.end_level, speed))
        return battery_curves
