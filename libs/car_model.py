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
            for car_model in car_models:
                if car_model.match(vin):
                    return car_model
            logger.warning("Can't get car model, please report an issue on github with your car model"
                           " and first ten letter of your VIN : %s", vin[:10])
        return CarModel("unknown", DEFAULT_BATTERY_POWER, DEFAULT_FUEL_CAPACITY)

    @staticmethod
    def find_model_by_name(name):
        for car_model in car_models:
            if car_model.name == name:
                return car_model
        return None


class ElecModel(CarModel):
    # pylint: disable=too-many-arguments
    def __init__(self, name, battery_power, abrp_name=None, reg=None,
                 max_elec_consumption=DEFAULT_MAX_ELEC_CONSUMPTION):
        super().__init__(name, battery_power, 0, abrp_name, reg, max_elec_consumption, 0)


car_models = [
    ElecModel("e-208", 46, "peugeot:e208:20:50", r"VR3UHZKX.*"),
    ElecModel("e-2008", 46, "peugeot:e2008:20:48", r"VR3UKZKX.*"),
    ElecModel("e-Spacetourer", 46, "peugeot:etraveler:21:50:citroen", r"VF7VZZKX.*"),
    ElecModel("e-Traveller", 46, "peugeot:etraveler:21:50", r"VF3VZZKX.*"),
    ElecModel("corsa-e", 46, "opel:corsae:20:50", r"VXKUHZKX.*"),
    ElecModel("DS3 Crossback e-tense", 46, "ds:3crossback:20:48", r"VR1UJZKX.*"),  # VR1UJZKXZL
    ElecModel("Mokka-e", 46, "opel:mokkae:20:48", r"VXKUKZKX.*"),  # VXKUKZKXZM
    ElecModel("Zaphira-e", 68, "peugeot:etraveler:21:75:opel", r"VXEVZZKX.*"),  # VXEVZZKXZMZ
    ElecModel("E-C4", 46, "citroen:ec4:21:50", r"VR7BCZKX.*"),  # VR7BCZKXCM
    CarModel("SUV 3008 Hybrid 225", 13.2, 43, reg=r"VF3M4DGZ.*"),  # VF3M4DGZUMS
    CarModel("308", 0, 56, reg=r"VF3L35GG.*"),
    CarModel("208", 0, 44, reg=r"VR3UPHN[SE].*"),  # VR3UPHNSSM VR3UPHNEKM
    CarModel("2008", 0, 44, reg=r"VR3USHNS.*"),  # VR3USHNSKM
    CarModel("2008 II", 0, 45, reg=r"VR3USHNK.*"),  # VR3USHNKKL
    CarModel("SUV 5008 II", 0, 56, reg=r"VF3MRHNS.*"),  # vf3mrhnsum
    CarModel("SUV 5008 II 2018", 0, 56, reg=r"VF3MRHNY.*"),  # VF3MRHNYHH
    CarModel("N5008 GT-LINE 1.6L", 0, 60, reg=r"VF3MCBHZ.*"),  # VF3MCBHZWJ
    CarModel("C5 Aircross Hybrid", 13.2, 43, reg=r"VR7A4DGZ.*"),  # VR7A4DGZSM
    CarModel("DS7 Crossback E-Tense 300 4x4", 11.5, 43, reg="VR1J45GB.*"),  # VR1J45GBUM VR1J45GBUL VR1J45GBUK
    CarModel("508 SW Hybrid", 11.5, 45, reg=r"VR3F4DGZ.*"),  # VR3F4DGZTL
    CarModel("508 Hybrid", 11.5, 43, reg=r"VR3F3DGZ.*"),  # VR3F3DGZTM
    CarModel("508 SW 2.0 HDI 163CV", 0, 72, reg=r"VF38ERHH.*"),  # VF38ERHH
    CarModel("Grandland X Hybrid", 13.2, 43, reg=r"W0VZ4DGZ.*"),  # W0VZ4DGZ2L
    CarModel("Grandland X Hybrid 4x4", 13.2, 43, reg=r"W0VZ45GB.*")  # W0VZ45GB3L
]
