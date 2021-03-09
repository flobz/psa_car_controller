import json
from copy import copy

from MyLogger import logger

ENERGY_CAPACITY = {'SUV 3008': {'BATTERY_POWER': 10.8, 'FUEL_CAPACITY': 43},
                   'C5 Aircross': {'BATTERY_POWER': 10.8, 'FUEL_CAPACITY': 43},
                   'e-208': {'BATTERY_POWER': 46, 'FUEL_CAPACITY': 0},
                   'e-2008': {'BATTERY_POWER': 46, 'FUEL_CAPACITY': 0}
                   }
DEFAULT_BATTERY_POWER = 46
DEFAULT_FUEL_CAPACITY = 0


class Car:
    def __init__(self, vin, vehicle_id, brand, label="unknown", battery_power=None, fuel_capacity=None):
        self.vin = vin
        self.vehicle_id = vehicle_id
        self.label = label
        self.brand = brand
        self.battery_power = None
        self.fuel_capacity = None
        self.set_energy_capacity(battery_power, fuel_capacity)
        self.status = None

    def set_energy_capacity(self, battery_power = None, fuel_capacity = None):
        if battery_power is not None and fuel_capacity is not None:
            self.battery_power = battery_power
            self.fuel_capacity = fuel_capacity
        elif self.label in ENERGY_CAPACITY:
            self.battery_power = ENERGY_CAPACITY[self.label]["BATTERY_POWER"]
            self.fuel_capacity = ENERGY_CAPACITY[self.label]["FUEL_CAPACITY"]
        else:
            logger.warning("Can't get car model please check cars.json")
            self.battery_power = DEFAULT_BATTERY_POWER
            self.fuel_capacity = DEFAULT_FUEL_CAPACITY

    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)

    def to_dict(self):
        car_dict = copy(self.__dict__)
        car_dict.pop("status")
        return car_dict

    def __str__(self):
        return str(self.to_dict())

class Cars(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def get_car_by_vin(self, vin) -> Car:
        for car in self:
            if car.vin == vin:
                return car
        return None

    def get_car_by_id(self, vehicle_id) -> Car:
        for car in self:
            if car.vehicle_id == vehicle_id:
                return car
        return None

    def add(self, car: Car):
        if self.get_car_by_id(car.vehicle_id) is None:
            self.append(car)

    @classmethod
    def from_json(cls, data: list):
        cars = list(map(Car.from_json, data))
        return cls(cars)

    def __str__(self):
        return str(list(map(str, self)))

    def save_cars(self, name="cars.json"):
        config_str = json.dumps(self, default=lambda car: car.to_dict(), sort_keys=True, indent=4)
        with open(name, "w") as f:
            f.write(config_str)

    @staticmethod
    def load_cars(name="cars.json"):
        try:
            with open(name, "r") as f:
                json_str = f.read()
                return Cars.from_json(json.loads(json_str))
        except (FileNotFoundError, TypeError):
            return Cars()
