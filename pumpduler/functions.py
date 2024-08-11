import datetime
from .import config


def get_datetime():
    return datetime.datetime.now(config.TIMEZONE)
