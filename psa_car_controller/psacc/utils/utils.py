import logging
import socket

import requests

logger = logging.getLogger(__name__)
TIMEOUT_IN_S = 10


def get_temp(latitude: str, longitude: str, api_key: str) -> float:
    try:
        if not (latitude is None or longitude is None or api_key is None):
            weather_rep = requests.get("https://api.openweathermap.org/data/2.5/onecall",
                                       params={"lat": latitude, "lon": longitude,
                                               "exclude": "minutely,hourly,daily,alerts",
                                               "appid": api_key,
                                               "units": "metric"},
                                       timeout=TIMEOUT_IN_S)
            temp = weather_rep.json()["current"]["temp"]
            logger.debug("Temperature :%fc", temp)
            return temp
    except ConnectionError:
        logger.error("Can't connect to openweathermap :", exc_info=True)
    except KeyError:
        logger.error("Unable to get temperature from openweathermap :", exc_info=True)
    return None


def is_port_in_use(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
