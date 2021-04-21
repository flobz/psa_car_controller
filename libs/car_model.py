import re

from mylogger import logger

DEFAULT_BATTERY_POWER = 46
DEFAULT_FUEL_CAPACITY = 0
DEFAULT_MAX_ELEC_CONSUMPTION = 70
DEFAULT_MAX_FUEL_CONSUMPTION = 30


class CarModel:
    # pylint: disable=too-many-arguments
    def __init__(self, name, battery_power, fuel_capacity, abrp_name=None, reg=None,
                 max_elec_consumption=DEFAULT_MAX_ELEC_CONSUMPTION, max_fuel_consumption=DEFAULT_MAX_FUEL_CONSUMPTION):
        self.name = name
        self.battery_power = battery_power
        self.fuel_capacity = fuel_capacity
        self.abrp_name = abrp_name
        self.reg = reg
        self.max_elec_consumption = max_elec_consumption
        self.max_fuel_consumption = max_fuel_consumption

    def match(self, vin):
        if self.reg is None:
            return False
        return re.match(self.reg, vin) is not None

    @staticmethod
    def find_model_by_vin(vin):
        for carmodel in carmodels:
            if carmodel.match(vin):
                return carmodel
        logger.warning("Can't get car model, please report an issue on github with your car model"
                       " and first ten letter of your VIN")
        return CarModel("unknown", DEFAULT_BATTERY_POWER, DEFAULT_FUEL_CAPACITY)

    @staticmethod
    def find_model_by_name(name):
        for carmodel in carmodels:
            if carmodel.name == name:
                return carmodel
        return None


class ElecModel(CarModel):
    # pylint: disable=too-many-arguments
    def __init__(self, name, battery_power, abrp_name=None, reg=None,
                 max_elec_consumption=DEFAULT_MAX_ELEC_CONSUMPTION):
        super().__init__(name, battery_power, 0, abrp_name, reg, max_elec_consumption, 0)


carmodels = [
    ElecModel("e-208", 46, "peugeot:e208:20:50", r"VR3UHZKX.*"),
    ElecModel("e-2008", 46, "peugeot:e2008:20:48", r"VR3UKZKX.*"),
    ElecModel("e-Spacetourer", 46, "peugeot:etraveler:21:50:citroen", r"VF7VZZKX.*"),
    ElecModel("corsa-e", 46, "opel:corsae:20:50", r"VXKUHZKX.*"),
    CarModel("SUV 3008", 10.8, 43),
    CarModel("C5 Aircross", 10.8, 43)
]
