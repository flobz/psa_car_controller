import traceback
from functools import wraps
from threading import Semaphore, Timer

import requests
import socket

from MyLogger import logger


def get_temp(latitude: str, longitude: str, api_key: str) -> float:
    try:
        if not (latitude is None or longitude is None or api_key is None):
            weather_rep = requests.get("https://api.openweathermap.org/data/2.5/onecall",
                                       params={"lat": latitude, "lon": longitude,
                                               "exclude": "minutely,hourly,daily,alerts",
                                               "appid": api_key,
                                               "units": "metric"})
            temp = weather_rep.json()["current"]["temp"]
            logger.debug("Temperature :%fc", temp)
            return temp
    except ConnectionError:
        logger.error("Can't connect to openweathermap :%s", traceback.format_exc())
    except KeyError:
        logger.error("Unable to get temperature from openweathermap :%s", traceback.format_exc())
    return None


def rate_limit(limit, every):
    def limit_decorator(fn):
        semaphore = Semaphore(limit)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            semaphore.acquire()
            try:
                return fn(*args, **kwargs)
            finally:  # don't catch but ensure semaphore release
                timer = Timer(every, semaphore.release)
                timer.setDaemon(True)  # allows the timer to be canceled on exit
                timer.start()

        return wrapper

    return limit_decorator


def is_port_in_use(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0
