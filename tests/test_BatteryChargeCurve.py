import unittest

from psa_car_controller.psacc.application.battery_charge_curve import BatteryChargeCurve
from psa_car_controller.psacc.model.battery_curve import BatteryCurveDto
from psa_car_controller.psacc.model.car import Car
from psa_car_controller.psacc.model.charge import Charge
from tests.utils import date0, date1, date2

vin1 = "VRAAAAAAA"
car1 = Car(vin1, "1sdfdksnfk222", "Peugeot", "208", 46, 0)


class TestBatteryChargeCurve(unittest.TestCase):

    def test_battery_curve_dto(self):
        battery_curve = [BatteryCurveDto(date0, 0, 20, 60),
                         BatteryCurveDto(date1, 60, 20, 100),
                         BatteryCurveDto(date2, 80, 20, 120)]
        charge = Charge(date0, date2, vin1, 0, 80)
        res = [point.speed for point in BatteryChargeCurve.dto_to_battery_curve(car1, charge, battery_curve)]
        self.assertEqual([32.5, 14.5, 0], res)

    def test_battery_curve_dto_zero(self):
        battery_curve = [BatteryCurveDto(date0, 0, 20, 0)]
        level_at_end = 80
        charge = Charge(date0, date2, vin1, 0, level_at_end)
        res = BatteryChargeCurve.dto_to_battery_curve(car1, charge, battery_curve)
        self.assertEqual(0, res[0].level)
        self.assertEqual(level_at_end, res[1].level)
        self.assertAlmostEqual(55.19, res[1].speed, places=1)
