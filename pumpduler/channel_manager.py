import typing
from .client import Client
from .channel import Channel
from .logger import logger


class ChannelManager:
    """
    Channel manager stores the all channels in the object and provides
    methods for subscribing and unsubscribing it and also provide method
    to broadcast a message to a channel, all of this methods are
    abstraction over the `Channel` methods to manage the channels and
    when these methods are called the corresponding `Channel` object
    methods are called.
    """
    def __init__(self) -> None:
        self._channels: typing.Dict[str, Channel] = {}

    def channels_count(self) -> int:
        """
        Returns:
            (int) number of channels
        """
        return len(self._channels)

    def get_channel_names(self) -> typing.List[str]:
        """
        Returns:
            (list(str)) list of channel names
        """
        return list(self._channels.keys())

    def subscribe(self, name: str, client: Client) -> None:
        """"
        Subscribe to a channel, this will create a new channel if
        it's not created.

        Args:
            name (str): channel name
            client (pumpduler.client.Client): client object

        Returns:
            (None)
        """
        if name not in self._channels:
            logger.debug(f"Channel:{name} is created!")
            self._channels[name] = Channel(name=name)
        self._channels[name].subscribe(client)

    def get_subscribed_channels(self, client: Client) -> typing.List[str]:
        """
        Get client's subscribed channels.

        Args:
            client (pumpduler.client.Client): client object

        Returns:
            (list(str)) subscribed channel names
        """
        channels = []
        for channel in self._channels:
            if client in self._channels[channel].subscribers:
                channels.append(channel)
        return channels

    def unsubscribe(self, name: str, client: Client) -> None:
        """
        Unsubscribes a channel for client and also removes the channel
        from the list if there's no subscriber after removing the
        client.

        Args:
            name (str): channel name
            client (pumpduler.client.Client): client object

        Returns:
            (None)
        """
        if name in self._channels:
            self._channels[name].unsubscribe(client)
            if self._channels[name].subscribers_count() == 0:
                logger.debug(f"Channel:{name} is destroyed!")
                self._channels.pop(name)

    def broadcast_message(
        self,
        channel_names: typing.List[str],
        message_type: str,
        message_data: typing.Any
    ):
        """
        Send a message to clients connected to the channels.

        Args:
            channel_names (list(str)): list of channel names
            message_type (str): type of the message, see `pumpduler.constants.SeverToClientMessageTypes`
            message_data (Any): this can be any that a parser can dump and load

        Returns:
            (None)
        """
        logger.info(f"[:ChannelManager] broadcast message with type:{message_type} in channels:{channel_names}")
        for channel_name in channel_names:
            if channel_name in self._channels:
                channel = self._channels[channel_name]
                channel.broadcast(
                    message_type=message_type,
                    message_data=message_data
                )
