import socket
import typing
from .constants import Actions, SeverToClientMessageTypes
from .functions import get_datetime
from .message import PumpdulerMessage
from .logger import logger

if typing.TYPE_CHECKING:
    from .client_manager import ClientManager


class Client:
    """
    Holds socket object and provides the methods send and process the message.
    """
    def __init__(self, sock: socket.socket, client_manager: 'ClientManager'):
        self._sock: socket.socket = sock
        self.client_manager: 'ClientManager' = client_manager
        self.timestamp: float = get_datetime().timestamp()
        self.sent_data_size: int = 0
        self.received_data_size: int = 0
        self.action_func_mapping = {
            Actions.PING: self._ping,
            Actions.SUBSCRIBE: self._subscribe,
            Actions.UNSUBSCRIBE: self._unsubscribe,
            Actions.SERVER_INFO: self._server_info,
            Actions.PUBLISH: self._publish,
            Actions.ADD_TIME_EVENT: self._add_time_event,
        }

    def _ping(self, *args, **kwargs):
        self.send_message(SeverToClientMessageTypes.MESSAGE, "PONG")

    def _subscribe(self, channel_name: str, *args, **kwargs):
        self.client_manager.channel_manager.subscribe(channel_name, self)

    def _unsubscribe(self, channel_name: str, *args, **kwargs):
        self.client_manager.channel_manager.unsubscribe(channel_name, self)

    def _server_info(self, *args, **kwargs):
        server = self.client_manager.server
        response_data = {
            "started_time": server.init_time,
            "uptime": round(get_datetime().timestamp() - server.init_time, 4),
            "clients": self.client_manager.clients_count(),
            "channels_num": self.client_manager.channel_manager.channels_count(),
            "channels": self.client_manager.channel_manager.get_channel_names(),
            "time_events_num": self.client_manager.time_event_manager.time_events_count()
        }
        self.send_message(SeverToClientMessageTypes.MESSAGE, response_data)

    def _publish(self, channel_name: str, data: typing.Any, *args, **kwargs):
        self.client_manager.channel_manager.broadcast_message(
            channel_names=[channel_name],
            message_type=SeverToClientMessageTypes.PUBLISHED_EVENT,
            message_data=data
        )

    def _add_time_event(self, channel_name: str, exec_timestamp: float, data: typing.Any, *args, **kwargs):
        self.client_manager.time_event_manager.add_event(
            channel=channel_name,
            data=data,
            exec_dt=exec_timestamp
        )

    def process_message(self, data: typing.Dict[str, typing.Any]):
        """
        Process the message, checks for the action of the message and if
        there's no function in mapping for that then sends an error message
        to the current client, otherwise will execute corresponding function.

        Args:
            data (dict(str, Any)): data containing `action` key and other info

        Returns:
            (None)
        """
        action = data['action']     # see `pumpduler.constants.Actions`
        if action in self.action_func_mapping:
            func = self.action_func_mapping[action]
            func(**data)
        else:
            logger.info(f"Unknown or invalid action request: \"{action}\" from client:( {self._sock}")
            self.send_message(SeverToClientMessageTypes.ERROR_MESSAGE, {"message": f"Unknown action: {action}"})

    def send_message(self, message_type: str, message_data: typing.Any):
        """
        Send a message to the socket object of this client.

        Args:
            message_type (str): type of the message, see `pumpduler.constants.SeverToClientMessageTypes`
            message_data (Any): data to send that can dumped/parsed.

        Returns:
            (None)
        """
        dumped_message = PumpdulerMessage.dump({
            "type": message_type,
            "data": message_data
        })
        logger.debug(f"Message will be sent to client: {self._sock}")
        self._sock.sendall(dumped_message)
