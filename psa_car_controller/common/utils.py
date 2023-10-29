from functools import wraps
from threading import Semaphore, Timer
from typing import List

import requests
TIMEOUT_IN_S = 10


def rate_limit(limit, every):
    def limit_decorator(func):
        semaphore = Semaphore(limit)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if semaphore.acquire(blocking=False):  # pylint: disable=consider-using-with
                try:
                    return func(*args, **kwargs)
                finally:  # don't catch but ensure semaphore release
                    timer = Timer(every, semaphore.release)
                    timer.daemon = True
                    timer.start()
            else:
                raise RateLimitException

        return wrapper

    return limit_decorator


def parse_hour(s):
    s = s[2:]
    separators = ("H", "M", "S")
    res: List[int] = []
    for sep in separators:
        if sep in s:
            n, s = s.split(sep)
        else:
            n = 0
        res.append(int(n))
        if s.isnumeric():
            res.append(int(s))
            break
    if len(res) == 2:
        res.append(0)
    return res


class RateLimitException(Exception):
    pass


def get_positions(locations):
    latitude = 0
    longitude = 1
    locations_str = ""
    for line in locations:
        locations_str += str(line[latitude]) + "," + str(line[longitude]) + "|"
    locations_str = locations_str[:-1]
    res = requests.get("https://api.opentopodata.org/v1/srtm30m",
                       params={"locations": locations_str},
                       timeout=TIMEOUT_IN_S)
    return res.json()["results"]
