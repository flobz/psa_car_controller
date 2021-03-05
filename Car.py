import json

from MyLogger import logger

ENERGY_CAPACITY = {'SUV 3008': {'BATTERY_POWER': 10.8, 'FUEL_CAPACITY': 43},
                   '208': {'BATTERY_POWER': 46, 'FUEL_CAPACITY': 0},
                   '2008': {'BATTERY_POWER': 46, 'FUEL_CAPACITY': 0}
                   }
DEFAULT_BATTERY_POWER = 46
DEFAULT_FUEL_CAPACITY = 0


class Car:
    def __init__(self, vin, vehicle_id, brand, label="unknown", battery_power=None, fuel_capacity=None):
        self.vin = vin
        self.vehicle_id = vehicle_id
        self.label = label
        self.brand = brand
        if battery_power is not None and fuel_capacity is not None:
            self.battery_power = battery_power
            self.fuel_capacity = fuel_capacity
        elif label in ENERGY_CAPACITY:
            self.battery_power = ENERGY_CAPACITY[label]["BATTERY_POWER"]
            self.fuel_capacity = ENERGY_CAPACITY[label]["FUEL_CAPACITY"]
        else:
            logger.warn("Can't get car model please check cars.json")
            self.battery_power = DEFAULT_BATTERY_POWER
            self.fuel_capacity = DEFAULT_FUEL_CAPACITY

    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)

class Cars(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def get_car_by_vin(self, vin) -> Car:
        for car in self:
            if car.vin == vin:
                return car

    def get_car_by_id(self, vehicle_id) -> Car:
        for car in self:
            if car.vehicle_id == vehicle_id:
                return car

    def add(self, car: Car):
        if self.get_car_by_id(car.vehicle_id) is None:
            self.append(car)

    @classmethod
    def from_json(cls, data: list):
        students = list(map(Car.from_json, data))
        return cls(students)

    def __str__(self):
        return str(self.__dict__)

    def save_cars(self, name="cars.json"):
        config_str = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        with open(name, "w") as f:
            f.write(config_str)

    @staticmethod
    def load_cars(name="cars.json"):
        try:
            with open(name, "r") as f:
                json_str = f.read()
                return Cars.from_json(json.loads(json_str))
        except:
            return Cars()