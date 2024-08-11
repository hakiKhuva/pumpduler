"""
This file contains constants to use it in the module, they're
separated using classes according to their category.
"""

class Actions:
    """
    Type of action that client wants to perform on server.
    """
    PING = "ping"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PUBLISH = "publish"
    SERVER_INFO = "info"
    ADD_TIME_EVENT = "add_time_event"


class SeverToClientMessageTypes:
    """
    Type of the data server wants to send to the client.
    """
    TIME_EVENT = 'time_event'
    PUBLISHED_EVENT = 'published_event'
    MESSAGE = 'message'
    ERROR_MESSAGE = 'error_message'
