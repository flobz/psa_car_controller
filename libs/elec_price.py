from datetime import datetime, timezone, timedelta
import configparser
from statistics import mean, StatisticsError

from mylogger import logger



def set_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


class ElecPrice:
    currency = ""
    CONFIG_FILENAME = "config.ini"

    def __init__(self, day_price, night_price=None, nights_hours=None):
        self.day_price = set_number(day_price)
        self.night_price = set_number(night_price)
        self.nights_hour = None
        self.set_night_hour(nights_hours)
        self.config_filename = ElecPrice.CONFIG_FILENAME

    def set_night_hour(self, value):
        if value is not None and isinstance(value, list):
            self.nights_hour = []
            for hours in value:
                self.nights_hour.append(list(map(int, hours)))

    @staticmethod
    def compare_hour(date: datetime, hour, minute):
        if date.hour < hour:
            return False
        if date.hour == hour and date.minute < minute:
            return False
        return True

    def get_instant_price(self, date):
        local_date = utc_to_local(date)
        if self.night_price is None:
            return self.day_price
        if self.compare_hour(local_date, self.nights_hour[0][0], self.nights_hour[0][1]) or \
                not self.compare_hour(local_date, self.nights_hour[1][0], self.nights_hour[1][1]):
            return self.night_price
        return self.day_price

    def get_price(self, start, end, consumption):
        prices = []
        date = start
        res = None
        if not (start is None or end is None):
            while date < end:
                prices.append(self.get_instant_price(date))
                date = date + timedelta(minutes=30)
            try:
                res = round(consumption * mean(prices), 2)
            except (TypeError, StatisticsError):
                logger.error("Can't get_price of charge, check config")
        return res

    def is_enable(self):
        return self.day_price is not None

    @staticmethod
    def read_config(name=None):
        if name is None:
            name = ElecPrice.CONFIG_FILENAME
        config = configparser.ConfigParser()
        if len(config.read(name)) == 0:
            ElecPrice.write_default_config(name)
            config.read(name)
        elec_config = config["Electricity config"]
        if len(elec_config["night price"]) > 0:
            night_hours = []
            night_price = elec_config["night price"]
            for hour in [elec_config["night hour start"], elec_config["night hour end"]]:
                night_hours.append(hour.split("h"))
        else:
            night_hours = None
            night_price = None
        ElecPrice.currency = config["General"]["currency"]
        return ElecPrice(elec_config["day price"], night_price, night_hours)

    @staticmethod
    def write_default_config(name=None):
        if name is None:
            name = ElecPrice.CONFIG_FILENAME
        config = configparser.ConfigParser()
        config["General"] = {
            "currency": "€"
        }
        config["Electricity config"] = {
            "day price": "",
            "night price": "",
            "night hour start": "",
            "night hour end": ""
        }

        with open(name, "w") as f:
            config.write(f)
