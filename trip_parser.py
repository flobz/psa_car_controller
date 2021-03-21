from collections.abc import Callable
from Car import Car
from MyLogger import logger

LEVEL = "level"

LEVEL_FUEL = "level_fuel"


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
            res.append(start[energy] - end[energy])
        return res

    def __is_refuel_or_recharging(self, start, end, distance):
        decharge, fuel_consumption = self.get_level_consumption(start, end)
        if fuel_consumption < 0:
            logger.debugv("refuel detected")
            return True
        elif TripParser.is_recharging(decharge, fuel_consumption, distance):
            logger.debugv("charge detected")
            return True
        return False

    def __is_refuel(self, start, end, distance):
        decharge, fuel_consumption = self.get_level_consumption(start, end)
        if fuel_consumption < 0:
            logger.debugv("refuel detected")
            return True
        return False

    def __is_recharging(self, start, end, distance):
        decharge, fuel_consumption = self.get_level_consumption(start, end)
        return TripParser.is_recharging(decharge, fuel_consumption, distance)

    @staticmethod
    def is_recharging(decharge, _, distance):
        # A margin of two is set because battery level can increase with regeneration system or temperature change.
        # If distance is bigger than 0 but charge bigger than five there is probably missing point and we assume that
        # regeneration/temperature can't increase by 5 percent the battery level
        return decharge < -2 and (distance == 0 or decharge < -5)