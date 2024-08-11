import logging
from .config import CONSOLE_LOGGING, LOG_FILE, LOG_LEVEL
from .functions import log_timestamp_converter

log_formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
log_formatter.converter = log_timestamp_converter

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
