import datetime
from .import config


def get_datetime():
    return datetime.datetime.now(config.TIMEZONE)


def log_timestamp_converter(timestamp: float):
    dt = datetime.datetime.fromtimestamp(timestamp)
    dt = dt.astimezone(tz=config.TIMEZONE)
    return dt.timetuple()
