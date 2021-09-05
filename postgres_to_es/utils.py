import time
from datetime import datetime
from functools import wraps
from operator import itemgetter

from loggers import logger


def expo(base: float, factor: int, max_value: float):
    count = 0
    while True:
        res = factor * base ** count
        if res < max_value:
            yield res
            count += 1
        else:
            yield max_value


def backoff(exp, start_sleep_time=2, factor=2, border_sleep_time=10):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            delay = start_sleep_time
            exp_gen = expo(start_sleep_time, factor, border_sleep_time)
            while True:
                try:
                    return func(*args, **kwargs)
                except exp:
                    time.sleep(delay)
                    delay = next(exp_gen)
                    logger.error(
                        f"Не удалось выполнить подключение, повтор через {delay}s"
                    )

        return inner

    return func_wrapper


def coroutine(func):
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner


def get_value_by_key(key, data):
    if not data:
        return None
    names = ", ".join(map(itemgetter(key), data))
    return names if names else None


def get_update_time(redis_client):
    return (
        datetime.fromisoformat(redis_client.get("update_time").decode("utf-8"))
        if redis_client.get("update_time")
        else datetime.min
    )
