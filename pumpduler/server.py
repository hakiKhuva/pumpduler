import sys
import socket
import threading
from .import config
from .client_manager import ClientManager
from .functions import get_datetime
from .logger import logger


class Server(object):
    """
    The main class that creates and listens to the
    incoming requests and passes it to the corresponding
    client manager object.
    """
    def __init__(self) -> None:
        self._sock: socket.socket = None    # nothing for now
        self._client_manager: ClientManager = ClientManager(server=self)    # a client manager
        self._accept_connections_event = threading.Event()  # an event for stop/start accepting connections
        self._init_time = get_datetime().timestamp()    # timestamp of start

    @property
    def accept_connections_event(self) -> threading.Event:
        """
        Returns:
            (threading.Event) Event for stopping/starting accepting connections.
        """
        return self._accept_connections_event

    @property
    def init_time(self) -> float:
        """
        Returns:
            (float) timestamp of creating the `Server` object.
        """
        return self._init_time

    def _start_listen(self):
        """
        Start listening to the current socket object,
        this method will accept the connection and passed it
        to the client manager and the client manager will take
        care of process.

        This relies on an event `_accept_connections_event` to
        start/stop accepting incoming requests.
        """
        logger.debug("starting to listen")
        self.sock.listen(0)
        logger.info("waiting for clients to connect...")
        while True:
            self._accept_connections_event.wait()
            client_sock, addr = self.sock.accept()
            logger.info(f"Client connected: {client_sock} || {addr}")
            self._client_manager.add_client(client_sock)

    def _create(self):
        """
        Creates a socket object using `config` variables and
        also bind the address or unix socket file path to
        the socket.
        """
        logger.debug("creating socket object and binding")
        bind_address = None
        # check for the type of socket to be created and also set the correct
        # address to the variable.
        if config.HOST and config.PORT:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            bind_address = (config.HOST, config.PORT)
        elif config.UNIX_SOCKET_PATH is not None:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            bind_address = config.UNIX_SOCKET_PATH
        else:
            logger.error("Server socket type and/or binding is not defined!")
            sys.exit(1)

        logger.info(f"binding server to {bind_address}")
        try:
            self.sock.bind(bind_address)
        except OSError as e:
            logger.error(f"Failed to bind socket on: {bind_address}")
            logger.debug(f"Error occurred during binding: {bind_address}: {e}")
            sys.exit(1)
        self.accept_connections_event.set()

    def start(self):
        """
        Perform tasks for starting the server, in-short this will
        take care of everything required to start the server to
        accept the connections.
        """
        logger.info("Starting server")
        self._create()
        self._start_listen()
