import logging
import os

import ruamel.yaml
from typing import List

from psa_car_controller.psacc.model.car_model import ElecModel, CarModel, DEFAULT_BATTERY_POWER, DEFAULT_FUEL_CAPACITY
from psa_car_controller.psacc.utils.utils import Singleton

MODELS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/../resources/car_models.yml"
logger = logging.getLogger(__name__)


class CarModelRepository(metaclass=Singleton):
    def __init__(self):
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            models = f.read()
        yaml = ruamel.yaml.YAML()
        yaml.register_class(ElecModel)
        yaml.register_class(CarModel)
        self.models: List[CarModel] = yaml.load(models)

    def find_model_by_vin(self, vin) -> CarModel:
        if vin != "vin":
            for car_model in self.models:
                if car_model.match(vin):
                    return car_model
            logger.warning("Can't get car model, please report an issue on github with your car model"
                           " and first ten letter of your VIN : %s", vin[:10])
        return CarModel("unknown", DEFAULT_BATTERY_POWER, DEFAULT_FUEL_CAPACITY)

    def find_model_by_name(self, name) -> CarModel:
        for car_model in self.models:
            if car_model.name == name:
                return car_model
        return None
