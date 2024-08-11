import typing
import socket
import datetime
import io
from .message import PumpdulerMessage
from .config import MESSAGE_PARSER_CLASS, READ_SIZE
from .constants import Actions
from .exceptions import PumpdulerDisconnectError


class PumpdulerConnector:
    """
    Connector class to connect to the Pumpduler server and provides
    methods for all the actions that server supports.
    """
    def __init__(
        self,
        host: str,
        port: int,
        socket_filepath: typing.Optional[str] = None,
        parser_class: typing.Optional[str] = None,
        read_size: typing.Optional[int] = None
    ) -> None:
        """
        Args:
            host (str): server's host string
            port (int): server's port number
            socket_filepath (str, optional): path to the unix sock file, if specified then this will be considered first.
            parser_class (str, optional): path to the parser, defaults to `pumpduler.config.MESSAGE_PARSER_CLASS`
            read_size (int, optional): read size from the socket, defaults to `pumpduler.config.READ_SIZE`
        """
        self._socket: socket.socket = None
        self._address: typing.Tuple[str, int] = socket_filepath or (host, port)
        self._read_size: int = read_size or READ_SIZE
        self._buffer_io: io.BytesIO = io.BytesIO()
        PumpdulerMessage.setup(parser_class or MESSAGE_PARSER_CLASS)

    def ping(self):
        """
        Send ping action to the server and expected response for this
        is pong.

        Returns:
            (dict) response message from the server.
        """
        self._setup()
        dumped_message = PumpdulerMessage.dump({"action": Actions.PING})
        self._socket.sendall(dumped_message)
        return self.get_message()

    def subscribe(self, channel: str):
        """
        Subscribe to a channel, if channel does not exists if will
        be created.

        Args:
            channel (str): name of the channel to subscribe

        Returns:
            (None)
        """
        self._setup()
        dumped_message = PumpdulerMessage.dump({"action": Actions.SUBSCRIBE, "channel_name": channel})
        self._socket.sendall(dumped_message)

    def unsubscribe(self, channel: str):
        """
        Unsubscribe from the channel, if there's no other subscriber then
        the channel will be removed.

        Args:
            channel (str): name of the channel to unsubscribe

        Returns:
            (None)
        """
        self._setup()
        dumped_message = PumpdulerMessage.dump({"action": Actions.UNSUBSCRIBE, "channel_name": channel})
        self._socket.sendall(dumped_message)

    def info(self):
        """
        Get the information about the server such uptime, number
        of connected clients and etc.

        Returns:
            (dict) response message from the server.
        """
        self._setup()
        dumped_message = PumpdulerMessage.dump({"action": Actions.SERVER_INFO})
        self._socket.sendall(dumped_message)
        return self.get_message()

    def _get_response_from_sock(self, timeout: typing.Optional[int] = None):
        """
        Reads the data from socket and uses timeout if provided, this
        will add the data to the buffer object and stops when the character
        for the ending of the message is received.

        Args:
            timeout (int, optional): timeout to set to the socket, defaults to `None`

        Raises:
            pumpduler.exceptions.PumpdulerDisconnectError:
                if connection is disconnected.

        Returns:
            (bool) has received data
        """
        self._setup()
        self._socket.settimeout(timeout)
        current_point = self._buffer_io.tell()
        self._buffer_io.seek(0, io.SEEK_END)
        while True:
            try:
                chunk = self._socket.recv(self._read_size)
            except ConnectionError:
                raise PumpdulerDisconnectError("Connection is closed!")
            else:
                self._buffer_io.write(chunk)
                if PumpdulerMessage.MESSAGE_END_SIGN in chunk:
                    return True
            finally:
                self._buffer_io.seek(current_point)
                self._socket.settimeout(None)

    def get_message(self, timeout: typing.Optional[int] = None):
        """
        Returns a message from the server.

        Args:
            timeout (int, optional): timeout to pass to the socket.

        Raises:
            pumpduler.exceptions.PumpdulerDisconnectError:
                if connection is disconnected.

        Returns:
            (dict|None) message from the server or can be `None`.
        """
        has_response = self._get_response_from_sock(timeout=timeout)
        if has_response is not True:
            return
        data = self._buffer_io.readline()
        return PumpdulerMessage.load(data)

    def listen(self, timeout: typing.Optional[int] = None):
        """
        Starts an infinite loop and calls the `get_message` and if value other
        than `None` is returns then it will returned using yield.

        Args:
            timeout (int, optional): timeout to pass to the socket

        Raises:
            pumpduler.exceptions.PumpdulerDisconnectError:
                if connection is disconnected.
        """
        self._setup()
        while True:
            message = self.get_message(timeout=timeout)
            if message:
                yield message

    def publish(
        self,
        channel_name: str,
        data: typing.Union[typing.List, typing.Dict[str, typing.Union[str, int, float]], str, int, float],
    ):
        """
        Publish a message to the channel, if there's no subscriber to it
        then it will be sent but won't reach to any and won't cause any
        type of error.

        Args:
            channel_name (str): name of the channel to publish in
            data (Any): data to sent to the subscribers.

        Returns:
            (None)
        """
        self._setup()
        message = PumpdulerMessage.dump({
            "action": Actions.PUBLISH,
            "channel_name": channel_name,
            "data": data,
        })
        self._socket.sendall(message)

    def add_time_event(
        self,
        dt: typing.Union[datetime.datetime, float],
        channel_name: str,
        data: typing.Any
    ):
        """
        Adds a time event to the server, this will be executed on a specific
        time on the server and will be published to clients connected to
        that channel.

        Args:
            dt (datetime.datetime, float): timestamp or a datetime object.
            channel_name (str): name of the channel to publish this event in.
            data (Any): data to send to the subscribers.

        Returns:
            (None)
        """
        exec_timestamp = dt
        if isinstance(dt, datetime.datetime) is True:
            exec_timestamp = dt.timestamp()

        action = Actions.ADD_TIME_EVENT
        send_data = {
            "channel_name": channel_name,
            "action": action,
            "exec_timestamp": exec_timestamp,
            "data": data
        }
        message = PumpdulerMessage.dump(send_data)
        self._socket.sendall(message)

    def _setup(self):
        """
        Setup the socket object, connects and set
        """
        if self._socket is None:
            if isinstance(self._address, str) is True:
                self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            else:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect(self._address)
        self._socket.settimeout(None)

    def _shutdown(self):
        """
        Closes the socket connection.
        """
        if self._socket is not None:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()

    def close(self):
        """
        Close the connection to the server.
        """
        self._shutdown()

    def __enter__(self):
        self._setup()
        return self

    def __exit__(self, *args, **kwds):
        self._shutdown()
