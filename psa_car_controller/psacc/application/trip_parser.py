import logging
from collections.abc import Callable
from psa_car_controller.psacc.model.car import Car

LEVEL = 5

LEVEL_FUEL = 8

logger = logging.getLogger(__name__)


class TripParser:
    def __init__(self, car: Car):
        self.car = car
        self.get_level_consumption, self.is_refuel = self.__get_energy_method()

    def __get_energy_method(self) -> [Callable]:
        if self.car.is_electric():
            return TripParser.get_elec_consumption, self.__is_recharging
        if self.car.is_thermal():
            return TripParser.get_thermal_consumption, self.__is_refuel
        if self.car.is_hybrid():
            return TripParser.get_hybrid_consumption, self.__is_refuel_or_recharging
        raise ValueError("Unknown car type")

    @staticmethod
    def get_thermal_consumption(start, end):
        return [0, start[LEVEL_FUEL] - end[LEVEL_FUEL]]

    @staticmethod
    def get_elec_consumption(start, end):
        return [start[LEVEL] - end[LEVEL], 0]

    @staticmethod
    def get_hybrid_consumption(start, end):
        res = []
        for energy in [LEVEL, LEVEL_FUEL]:
            if start[energy] is not None and end[energy] is not None:
                res.append(start[energy] - end[energy])
            else:
                res.append(0)
        return res

    def __is_refuel_or_recharging(self, start, end, distance):
        decharge, fuel_consumption = self.get_level_consumption(start, end)
        if fuel_consumption < 0:
            logger.debugv("refuel detected")
            return True
        if TripParser.is_recharging(decharge, distance):
            logger.debugv("charge detected")
            return True
        return False

    # pylint: disable=unused-argument
    def __is_refuel(self, start, end, distance):
        fuel_consumption = self.get_level_consumption(start, end)[1]
        if fuel_consumption < 0:
            logger.debugv("refuel detected")
            return True
        return False

    def __is_recharging(self, start, end, distance):
        decharge = self.get_level_consumption(start, end)[0]
        return TripParser.is_recharging(decharge, distance)

    @staticmethod
    def is_recharging(decharge, distance):
        # A margin of two is set because battery level can increase with regeneration system or temperature change.
        # If distance is bigger than 0 but charge bigger than five there is probably missing point and we assume that
        # regeneration/temperature can't increase by 5 percent the battery level
        return decharge < -2 and (distance == 0 or decharge < -5)

    @staticmethod
    def is_low_speed(speed_average, duration):
        logger.debugv("Low speed detected")
        return speed_average < 0.2 and duration > 0.05
