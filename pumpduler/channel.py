import typing
import threading
from .client import Client
from .logger import logger


class Channel:
    """
    Channel contains client and provides methods with that channel
    manager can easily handles the client, this class holds the
    all clients and provides method to subscribe, unsubscribe and
    to broadcast a message.
    """
    def __init__(self, name: str) -> None:
        self._name: str = name
        self._clients: typing.List[Client] = []
        self._lock: threading.Lock = threading.Lock()

    @property
    def name(self) -> str:
        """
        Returns channel name
        """
        return self._name

    @property
    def subscribers(self) -> typing.List[Client]:
        """
        Returns list of subscribers to the channel.
        """
        return self._clients.copy()

    def subscribers_count(self) -> int:
        """
        Returns count of subscribers in this channel.
        """
        return len(self._clients)

    def subscribe(self, client: Client):
        """
        Adds a client to the list of subscribers of this channel.

        Args:
            client (pumpduler.client.Client): client object

        Returns:
            (None)
        """
        logger.info(f"{client._sock} wants to subscribe {self.name}")
        with self._lock:
            self._clients.append(client)
            logger.info(f"{client._sock} subscribed {self.name}")

    def unsubscribe(self, client: Client):
        """
        Removes the client from the list of subscribers of this channel.

        Args:
            client (pumpduler.client.Client): client object

        Returns:
            (None)
        """
        logger.info(f"{client._sock} wants to unsubscribe {self.name}")
        with self._lock:
            self._clients.remove(client)
            logger.info(f"{client._sock} unsubscribed {self.name}")

    def broadcast(self, message_type: str, message_data: typing.Any):
        """
        Send a message to all subscribers in this chanel.

        Args:
            message_type (str): type of the message, see `pumpduler.constants.SeverToClientMessageTypes`
            message_data (Any): message to send

        Returns:
            (None)
        """
        logger.debug(f"[:Channel] broadcasting a message with type: {message_type}")
        with self._lock:
            for client in self._clients:
                client.send_message(message_type=message_type, message_data=message_data)
