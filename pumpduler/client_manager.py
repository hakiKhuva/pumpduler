import typing
import socket
import threading
from .client import Client
from .time_event_manager import TimeEventManager
from .channel_manager import ChannelManager
from .message import PumpdulerMessage
from .logger import logger
from .import config

if typing.TYPE_CHECKING:
    from .server import Server


class ClientManager(object):
    """
    Client manager is for managing the clients within the
    server, this provides methods for adding, removing and
    handling the clients.

    When a client is added it is managed by this class without
    any other dependencies, this also manages the
    `accept_connections_event` of the server to restrict the
    size of the clients.
    """
    def __init__(self, server: 'Server') -> None:
        self._server: 'Server' = server     # server is required for the event `accept_connections_event`

        self._clients: typing.List[Client] = []     # all clients
        # lock is used when adding, removing the client
        self._clients_lock: threading.Lock = threading.Lock()

        self._channel_manager: ChannelManager = ChannelManager()    # manages the channels
        self._time_event_manager: TimeEventManager = TimeEventManager(client_manager=self)  # manages the time events

    @property
    def server(self) -> 'Server':
        return self._server

    @property
    def channel_manager(self) -> ChannelManager:
        return self._channel_manager

    @property
    def time_event_manager(self) -> TimeEventManager:
        return self._time_event_manager

    def clients_count(self) -> int:
        """
        Returns:
            (int) number of clients currently being handled.
        """
        return len(self._clients)

    def add_client(self, sock: socket.socket):
        """
        Add a client to the manager to manage it.

        Args:
            sock (socket.socket): socket connection of the client

        Returns:
            (None)
        """
        logger.debug(f"Adding client to the list: {sock}")
        with self._clients_lock:
            # creating client object and adding it to the list
            client = Client(
                sock=sock,
                client_manager=self,
            )
            self._clients.append(client)
            logger.debug(f"Client added to the list: {sock}")

            # checking if the number of clients are equal to the max client or not
            if len(self._clients) == config.MAX_CLIENTS:
                logger.info(f"Stopping accepting more connections, max clients count reached {len(self._clients)}/{config.MAX_CLIENTS}")
                self._server.accept_connections_event.clear()

            # creating a thread to handle the client and starting it.
            thread = threading.Thread(target=self._handle, args=(client,))
            thread.start()

    def _handle(self, client: Client):
        """
        Handles the client, this will receive the data from
        the socket and also checks for the processable data
        and passes the parsed data to the method of client
        object, this happens in a infinite loop and the loop
        is only stopped when client is disconnected.

        Args:
            client (pumpduler.client.Client): an object of `Client`

        Returns:
            (None)
        """
        logger.debug(f"Handling client: {client._sock}")
        sock = client._sock     # socket object of client
        data = b""  # buffer data
        while True:
            try:
                chunk = sock.recv(config.READ_SIZE)
            except ConnectionError:
                # client is disconnected, now remove the client
                logger.info(f"Client disconnected: {sock}")
                self._remove_client(client)
                break
            data += chunk   # add the chunk to data to complete it.
            while PumpdulerMessage.MESSAGE_END_SIGN in data:    # if the end char in data then process it
                # splitting it in two parts one is processable and another is other part of data to be reused
                processable_entity, data = data.split(PumpdulerMessage.MESSAGE_END_SIGN, 1)
                try:
                    # parse the data and send it to the client to process the message
                    processed_entity = PumpdulerMessage.load(processable_entity)
                except ValueError:
                    logger.error(f"Unprocessable entity (VALUE ERROR) client:({client._sock} chunk:({chunk} data:({data}")
                else:
                    client.process_message(processed_entity)
            if not chunk:   # there was no data in chunk, client is disconnected
                logger.info(f"Client disconnected: {sock}")
                self._remove_client(client)
                break

    def _remove_client(self, client: Client) -> None:
        """
        Remove the client from the list of client manager and also
        performs operations such starting to accept the connections
        by changing the value of event and removing the client from
        the subscribed channels.

        Args:
            client (pumpduler.client.Client): an object of `Client`

        Returns:
            (None)
        """
        with self._clients_lock:
            logger.debug(f"Removing client: {client._sock}")

            # check for the subscribed channels, if there're then remove the
            # client from those all channels
            subscribed_channels = self._channel_manager.get_subscribed_channels(client)
            if len(subscribed_channels) > 0:
                logger.debug(f"{client._sock} is subscribed to channels!")
                for channel in subscribed_channels:
                    logger.debug(f"Unsubscribe channel:( {channel} for client:( {client._sock}")
                    self._channel_manager.unsubscribe(channel, client)

            # removing client from the list
            self._clients.remove(client)
            # shutdown and closing connection
            client._sock.shutdown(socket.SHUT_RDWR)
            client._sock.close()
            logger.debug(f"Client {client._sock} removed.")

            # start accepting other connections if it's necessary
            if len(self._clients) < config.MAX_CLIENTS:
                if self._server.accept_connections_event.is_set() is False:
                    self._server.accept_connections_event.set()
                    logger.info(f"Starting accepting connections :) {self.clients_count()}/{config.MAX_CLIENTS}")
