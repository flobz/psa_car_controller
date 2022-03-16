from statistics import mean

from typing import List

from psacc.model.battery_curve import BatteryCurveDto
from psacc.model.car import Car
from psacc.model.charge import Charge
from psacc.repository.db import Database


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
        if len(battery_curves_dto) > 0:
            battery_capacity = battery_curves_dto[-1].level * car.battery_power / 100
            km_by_kw = 0.8 * battery_curves_dto[-1].autonomy / battery_capacity
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
        else:
            speed = car.get_charge_speed(charge.end_level - charge.start_level, (stop_at - start_date).total_seconds())
            battery_curves.append(BatteryChargeCurve(charge.start_level, speed))
            battery_curves.append(BatteryChargeCurve(charge.end_level, speed))
        return battery_curves
