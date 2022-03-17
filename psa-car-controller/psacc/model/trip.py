import logging
from statistics import mean
from typing import List

from geojson import MultiLineString, Feature

from .car import Car

logger = logging.getLogger(__name__)


class Points:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def list(self):
        return self.latitude, self.longitude


class Trip:
    def __init__(self):
        self.start_at = None
        self.end_at = None
        self.positions: List[Points] = []
        self.speed_average = None
        self.consumption = 0
        self.consumption_km = 0
        self.consumption_fuel = 0
        self.consumption_fuel_km = 0
        self.distance = None
        self.duration = None
        self.mileage = None
        self.car: Car = None
        self.altitude_diff = None
        self.temperatures = []
        self.id = None

    def add_points(self, latitude, longitude):
        self.positions.append(Points(latitude, longitude))

    def add_temperature(self, temp):
        self.temperatures.append(temp)

    def get_temperature(self):
        if len(self.temperatures) > 0:
            return float(mean(self.temperatures))
        return None

    def set_consumption(self, diff_level: float) -> float:
        if diff_level < 0:
            logger.debugv("trip has negative consumption")
            diff_level = 0
        self.consumption = diff_level * self.car.battery_power / 100
        try:
            self.consumption_km = 100 * self.consumption / self.distance  # kw/100 km
        except TypeError:
            raise ValueError("Distance not set") from TypeError
        return self.consumption_km

    def set_fuel_consumption(self, consumption) -> float:
        if self.distance is None:
            raise ValueError("Distance not set")
        if consumption < 0:
            logger.debugv("trip has negative fuel consumption")
        self.consumption_fuel = round(consumption * self.car.fuel_capacity / 100, 2)  # L
        self.consumption_fuel_km = round(100 * self.consumption_fuel / self.distance, 2)  # L/100 km
        return self.consumption_fuel_km

    def to_geojson(self):
        multi_line_string = MultiLineString(tuple(map(list, self.positions)))
        return Feature(geometry=multi_line_string, properties={"start_at": self.start_at, "end_at": self.end_at,
                                                               "average speed": self.speed_average,
                                                               "average consumption": self.consumption_km,
                                                               "average consumption fuel": self.consumption_fuel_km})

    def get_info(self):

        res = {"consumption_km": self.consumption_km, "start_at": self.start_at,
               "consumption_by_temp": self.get_temperature(), "positions": self.get_positions(),
               "duration": self.duration * 60, "speed_average": self.speed_average, "distance": self.distance,
               "mileage": self.mileage, "altitude_diff": self.altitude_diff, "id": self.id,
               "consumption": self.consumption
               }
        if self.car.has_battery():
            res["consumption_km"] = self.consumption_km

        if self.car.has_fuel():
            res["consumption_fuel_km"] = self.consumption_fuel_km

        return res

    def set_altitude_diff(self, start, end):
        try:
            self.altitude_diff = end - start
        except (NameError, TypeError):
            pass

    def get_positions(self):
        lat = []
        long = []
        for position in self.positions:
            lat.append(position.latitude)
            long.append(position.longitude)
        return {"lat": lat, "long": long}
