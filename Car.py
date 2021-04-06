import json
from copy import copy

from MyLogger import logger

ENERGY_CAPACITY = {'SUV 3008': {'BATTERY_POWER': 10.8, 'FUEL_CAPACITY': 43},
                   'C5 Aircross': {'BATTERY_POWER': 10.8, 'FUEL_CAPACITY': 43},
                   'e-208': {'BATTERY_POWER': 46, 'FUEL_CAPACITY': 0, "ABRP_NAME": "peugeot:e208:20:50"},
                   'e-2008': {'BATTERY_POWER': 46, 'FUEL_CAPACITY': 0, "ABRP_NAME": "peugeot:e2008:20:48"},
                   'corsa-e': {'BATTERY_POWER': 46, 'FUEL_CAPACITY': 0, "ABRP_NAME": "opel:corsae:20:50"}
                   }
DEFAULT_BATTERY_POWER = 46
DEFAULT_FUEL_CAPACITY = 0
DEFAULT_MAX_ELEC_CONSUMPTION = 70
DEFAULT_MAX_FUEL_CONSUMPTION = 30
DEFAULT_ABRP_NAME = "peugeot:e208:20:50"
CARS_FILE = "cars.json"


class Car:
    def __init__(self, vin, vehicle_id, brand, label="unknown", battery_power=None, fuel_capacity=None,
                 max_elec_consumption=None, max_fuel_consumption=None):
        self.vin = vin
        self.vehicle_id = vehicle_id
        self.label = label
        self.brand = brand
        self.battery_power = None
        self.fuel_capacity = None
        self.max_elec_consumption = 0  # kwh/100Km
        self.max_fuel_consumption = 0  # L/100Km
        self.set_energy_capacity(battery_power, fuel_capacity, max_elec_consumption, max_fuel_consumption)
        self.status = None

    def set_energy_capacity(self, battery_power=None, fuel_capacity=None, max_elec_consumption=None,
                            max_fuel_consumption=None):
        if battery_power is not None and fuel_capacity is not None:
            self.battery_power = battery_power
            self.fuel_capacity = fuel_capacity
        elif self.__get_model_name() is not None:
            model_name = self.__get_model_name()
            self.battery_power = ENERGY_CAPACITY[model_name]["BATTERY_POWER"]
            self.fuel_capacity = ENERGY_CAPACITY[model_name]["FUEL_CAPACITY"]
        else:
            logger.warning("Can't get car model please check %s", CARS_FILE)
            self.battery_power = DEFAULT_BATTERY_POWER
            self.fuel_capacity = DEFAULT_FUEL_CAPACITY
        if self.is_electric():
            self.max_fuel_consumption = 0
        else:
            self.max_fuel_consumption = max_fuel_consumption or DEFAULT_MAX_FUEL_CONSUMPTION
        if self.is_thermal():
            self.max_elec_consumption = 0
        else:
            self.max_elec_consumption = max_elec_consumption or DEFAULT_MAX_ELEC_CONSUMPTION

    def __get_model_name(self):
        if self.label in ENERGY_CAPACITY:
            return self.label
        if self.__is_opel_corsa():
            return "corsa-e"
        return None

    def __is_opel_corsa(self):
        return self.brand == "C" and self.label is None

    def is_electric(self) -> bool:
        return self.fuel_capacity == 0 and self.battery_power > 0

    def is_thermal(self) -> bool:
        return self.fuel_capacity > 0 and self.battery_power == 0

    def is_hybrid(self) -> bool:
        return self.fuel_capacity > 0 and self.battery_power > 0

    def get_status(self):
        if self.status is not None:
            return self.status
        logger.error("status of %s is None", self.vin)
        raise ValueError("status of %s is None")

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

    def save_cars(self, name=CARS_FILE):
        config_str = json.dumps(self, default=lambda car: car.to_dict(), sort_keys=True, indent=4)
        with open(name, "w") as f:
            f.write(config_str)

    @staticmethod
    def load_cars(name=CARS_FILE):
        try:
            with open(name, "r") as f:
                json_str = f.read()
                return Cars.from_json(json.loads(json_str))
        except (FileNotFoundError, TypeError) as e:
            logger.debug(e)
            return Cars()
