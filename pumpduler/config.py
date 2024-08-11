"""
Contains configurations for the server and other classes to send/receive
the information and etc.
"""

import logging
from datetime import timezone


HOST: str = "127.0.0.1"
PORT: int = 9090

UNIX_SOCKET_PATH: str = None # must be an absolute path

READ_SIZE: int = 10240   # read size of the socket
MAX_CLIENTS: int = 512    # maximum number of clients
MESSAGE_PARSER_CLASS: str = "pumpduler.parsers:JSON"     # parser class, must have `encode` and `decode` methods

TIMEZONE = timezone.utc     # timezone to use

CONSOLE_LOGGING: bool = True    # log to the console or not
LOG_FILE: str = None     # if wants to log to the file then path for it otherwise None, must be an absolute path
LOG_LEVEL: int = logging.INFO   # log level, this only works with the console logging, file logging log level is debug by default.
