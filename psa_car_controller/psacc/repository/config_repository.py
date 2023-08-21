import logging
import re
from datetime import datetime, timezone, timedelta
from statistics import mean, StatisticsError

from configupdater import ConfigUpdater
from pydantic import BaseModel
from typing import List

from psa_car_controller.psacc.application.battery_charge_curve import BatteryChargeCurve
from psa_car_controller.psacc.model.charge import Charge

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = """[General]
currency = €
# define format for data export, can be csv or xlsx
export_format = csv
# minimum trip length in km so it's added to stats and map in website
minimum trip length =
# for future use
length unit = km
[Electricity config]
# price by kw/h
day price =
night price =
# ex: 22h30
night hour start =
# ex: 6h00
night hour end =
dc charge price =
high speed dc charge price =
# minimum power in kW that should be delivered during a charge so it can be considered as a high speed charger
high speed dc charge threshold =
charger efficiency =
"""


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def replace_key_underscore_by_space(obj, key):
    new_obj = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            new_obj[k.replace("_", " ")] = replace_key_underscore_by_space(v, key)
        else:
            new_obj[k.replace("_", " ")] = v
    return new_obj


class Hour:
    reg = re.compile(r"([0-9]{1,2})h([0-9]{1,2})")

    def __init__(self, hours: int, minutes: int):
        self.hours = hours
        self.minutes = minutes

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        if len(v) == 0:
            return None

        m = Hour.reg.fullmatch(v.lower())
        if not m:
            raise ValueError('invalid hour format')
        return cls(int(m.group(1)), int(m.group(2)))

    def __repr__(self):
        return '{}h{}'.format(self.hours, self.minutes)


currency = ""
CONFIG_FILENAME = "config.ini"


class GeneralConfig(BaseModel):
    currency: str = "€"
    length_unit: str = "km"
    minimum_trip_length: float = 10
    export_format = "csv"


class ElectricityPriceConfig(BaseModel):
    day_price: float = 0.15
    night_price: float = None
    night_hour_start: Hour = None
    night_hour_end: Hour = None
    dc_charge_price: float = None
    high_speed_dc_charge_price: float = None
    high_speed_dc_charge_threshold: float = None
    charger_efficiency: float = 0.8942

    @staticmethod
    def compare_hour(date: datetime, hour, minute):
        if date.hour < hour:
            return False
        if date.hour == hour and date.minute < minute:
            return False
        return True

    def is_nigh_hour_enabled(self):
        return self.night_hour_start and self.night_hour_end and self.night_price

    def get_instant_price(self, date):
        local_date = utc_to_local(date)
        if self.night_price is None:
            return self.day_price
        if self.compare_hour(local_date, self.night_hour_start.hours, self.night_hour_start.minutes) or \
                not self.compare_hour(local_date, self.night_hour_end.hours, self.night_hour_end.minutes):
            return self.night_price
        return self.day_price

    def _get_dc_charge_price(self, charge: Charge, battery_charge_curves: List[BatteryChargeCurve]):
        max_consumption = sum(battery_charge_curve.speed for battery_charge_curve in battery_charge_curves)
        total_consumption = charge.kw
        if self.high_speed_dc_charge_threshold and max_consumption > self.high_speed_dc_charge_threshold:
            return self.high_speed_dc_charge_price * total_consumption
        return self.dc_charge_price * total_consumption

    def _get_ac_charge_price(self, start, end, consumption):
        prices = []
        date = start
        res = None
        if not (start is None or end is None):
            while date < end:
                prices.append(self.get_instant_price(date))
                date = date + timedelta(minutes=30)
            try:
                res = round(consumption * mean(prices) / self.charger_efficiency, 2)
            except (TypeError, StatisticsError):
                logger.error("Can't get_price of charge, check config")
        return res

    def get_price(self, charge: Charge, battery_charge_curves: List[BatteryChargeCurve]):
        if charge.charging_mode.DC and self.dc_charge_price:
            return self._get_dc_charge_price(charge, battery_charge_curves)
        return self._get_ac_charge_price(charge.start_at, charge.stop_at, charge.kw)

    def is_enable(self):
        return self.day_price is not None


class ConfigRepository(BaseModel):
    General: GeneralConfig
    Electricity_config: ElectricityPriceConfig

    @staticmethod
    def _read_file(name):
        if name is None:
            name = CONFIG_FILENAME
        with open(name, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def read_config(name=None) -> 'ConfigRepository':
        try:
            config_str = ConfigRepository._read_file(name)
            config = ConfigUpdater(allow_no_value=True)
            config.read_string(config_str)
            return ConfigRepository.config_file_to_dto(config)
        except FileNotFoundError:
            config = ConfigRepository.config_file_to_dto(ConfigRepository.get_default_config())
            config.write_config()
            return config

    @staticmethod
    def get_default_config():
        config = ConfigUpdater(allow_no_value=True)
        config.read_string(DEFAULT_CONFIG)
        return config

    def config_dto_to_config_file(self, config):
        res = replace_key_underscore_by_space(self.dict(), None)
        for section, option in res.items():
            for key, value in option.items():
                config[section][key] = value

        return config

    def write_config(self, name=None):
        if name is None:
            name = CONFIG_FILENAME
        config_to_write = ConfigRepository.get_default_config()
        self.config_dto_to_config_file(config_to_write)
        self._write(name, config_to_write)

    @staticmethod
    def _write(name, config):
        with open(name, "w", encoding="utf-8") as f:
            config.write(f)

    @staticmethod
    def config_file_to_dto(config) -> 'ConfigRepository':
        new_dict = {}
        for section in config:
            new_section = section.replace(" ", "_")
            new_dict[new_section] = {}
            for option in config[section]:
                new_option = option.replace(" ", "_")
                value = config[section][option].value
                if value and len(value) > 0:
                    new_dict[new_section][new_option] = value

        config_obj = ConfigRepository(**new_dict)
        return config_obj
