import json
from copy import copy

from mylogger import logger
from libs.car_model import CarModel
from libs.car_status import CarStatus

# pylint: disable=too-many-instance-attributes,too-many-arguments
class Car:
    def __init__(self, vin, vehicle_id, brand, label=None, battery_power=None, fuel_capacity=None,
                 max_elec_consumption=None, max_fuel_consumption=None, abrp_name=None):
        self.vin = vin
        model = None
        if label is not None:
            model = CarModel.find_model_by_name(label)
        if model is None:
            model = CarModel.find_model_by_vin(self.vin)
            label = model.name
        self.vehicle_id = vehicle_id
        self.label = label
        self.brand = brand
        self._status = None
        self.abrp_name = abrp_name or model.abrp_name
        self.battery_power = battery_power or model.battery_power
        self.fuel_capacity = fuel_capacity or model.fuel_capacity
        self.max_elec_consumption = max_elec_consumption or model.max_elec_consumption  # kwh/100Km
        self.max_fuel_consumption = max_fuel_consumption or model.max_fuel_consumption  # L/100Km

    def set_model_name(self, name):
        self.label = name

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
        car_dict.pop("_status")
        return car_dict

    def __str__(self):
        return str(self.to_dict())

    def get_abrp_name(self):
        if self.abrp_name is not None:
            return self.abrp_name
        raise ValueError("ABRP model is not set")

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: CarStatus):
        self._status = value
        if self._status is not None and self.status.__class__ != CarStatus:
            self._status.__class__ = CarStatus
            self._status.correct()


class Cars(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.config_filename = "../cars.json"

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

    def save_cars(self, name=None):
        if name is None:
            name = self.config_filename
        config_str = json.dumps(self, default=lambda car: car.to_dict(), sort_keys=True, indent=4)
        with open(name, "w") as file:
            file.write(config_str)

    @staticmethod
    def load_cars(name=None):
        if name is None:
            name = Cars().config_filename
        try:
            with open(name, "r") as file:
                json_str = file.read()
                cars = Cars.from_json(json.loads(json_str))
                cars.config_filename = name
                cars.save_cars()
                return cars
        except (FileNotFoundError, TypeError) as ex:
            logger.debug(ex)
            return Cars()
