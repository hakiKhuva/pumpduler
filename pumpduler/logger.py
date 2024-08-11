import logging
from .config import CONSOLE_LOGGING, LOG_FILE, LOG_LEVEL, TIMEZONE
from datetime import datetime

log_formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
def converter(timestamp: float):
    dt = datetime.fromtimestamp(timestamp)
    dt = dt.astimezone(tz=TIMEZONE)
    return dt.timetuple()

log_formatter.converter = converter

logger = logging.getLogger(__name__)

if CONSOLE_LOGGING is True:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    logger.setLevel(LOG_LEVEL)

if LOG_FILE is not None:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
