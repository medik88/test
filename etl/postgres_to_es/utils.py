import logging
import typing
from functools import wraps
from logging.config import fileConfig

from config import settings

fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("etl.utils")


def coroutine(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner


def backoff_hdlr(details: dict) -> None:
    logger.info(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function '{target.__name__}'".format(**details)
    )
