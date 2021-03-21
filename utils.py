import traceback
from functools import wraps
from threading import Semaphore, Timer

import requests

from MyLogger import logger


def get_temp(latitude, longitude, api_key):
    try:
        weather_rep = requests.get("https://api.openweathermap.org/data/2.5/onecall",
                                   params={"lat": latitude, "lon": longitude,
                                           "exclude": "minutely,hourly,daily,alerts",
                                           "appid": api_key,
                                           "units": "metric"})
        temp = weather_rep.json()["current"]["temp"]
        logger.debug("Temperature :%fc", temp)
    except ConnectionError:
        logger.error("Can't connect to openweathermap :%s", traceback.format_exc())
    except KeyError:
        logger.error("Unable to get temperature from openweathermap :%s", traceback.format_exc())


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