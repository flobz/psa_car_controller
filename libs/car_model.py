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
        if vin != "vin":
            for carmodel in carmodels:
                if carmodel.match(vin):
                    return carmodel
            logger.warning("Can't get car model, please report an issue on github with your car model"
                           " and first ten letter of your VIN : %s", vin[:10])
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
    ElecModel("DS3 Crossback e-tense", 46, "ds:3crossback:20:48", r"VR1UJZKX.*"), # VR1UJZKXZL
    # Use corsa in abrp because Mokka isn't available
    ElecModel("Mokka-e", 46, "opel:corsae:20:50", r"VXKUKZKX.*"),  # VXKUKZKXZM
    ElecModel("Zaphira-e", 68, "peugeot:etraveler:21:75:opel", r"VXEVZZKX.*"),  # VXEVZZKXZMZ
    ElecModel("E-C4", 46, "citroen:ec4:21:50", r"VR7BCZKX.*"),  # VR7BCZKXCM
    CarModel("SUV 3008", 10.8, 43),
    CarModel("308", 0, 56, reg=r"VF3L35GG.*"),
    CarModel("208", 0, 44, reg=r"VR3UPHNS.*"),  # VR3UPHNSSM
    CarModel("2008", 0, 44, reg=r"VR3USHNS.*"),  # VR3USHNSKM
    CarModel("SUV 5008 II", 0, 56, reg=r"VF3MRHNS.*"),  # vf3mrhnsum
    CarModel("SUV 5008 II 2018", 0, 56, reg=r"VF3MRHNY.*"),  #  VF3MRHNYHH
    CarModel("C5 Aircross", 10.8, 43),
    CarModel("DS7 Crossback E-Tense", 11.5, 43, reg="VR1J45GBUK.*"),
    CarModel("DS7 Crossback E-Tense 300 4x4", 11.5, 43, reg=" VR1J45GBUL.*"),
    CarModel("508 SW Hybrid", 11.5, 45, reg=r"VR3F4DGZ.*"), # VR3F4DGZTL
    CarModel("Grandland X Hybrid", 13.2, 43, reg=r"W0VZ4DGZ.*"), #W0VZ4DGZ2L
    CarModel("Grandland X Hybrid 4x4", 13.2, 43, reg=r"W0VZ45GB.*") #W0VZ45GB3L
]
