from functools import wraps
from threading import Semaphore, Timer
from typing import List


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
                    timer.setDaemon(True)  # pylint: disable=deprecated-method
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
