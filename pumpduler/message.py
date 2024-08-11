import typing
import importlib
import threading
from .import config


class PumpdulerMessage:
    """
    This class provides methods to dump and load the object in a
    specific format, this will also import the parser class using
    the string in config, uses `config.MESSAGE_PARSER_CLASS`
    """
    MESSAGE_END_SIGN = b"\n"
    IMPORT_LOCK = threading.Lock()
    parser = None

    @staticmethod
    def setup(parser_path: typing.Optional[str] = None):
        """
        Method to import the parser class, this will only import if
        the `parser` value is `None`.

        Args:
            parser_path (str, optional): path to the parser if provided then `config.MESSAGE_PARSER_CLASS` won't be used.

        Returns:
            (None)
        """
        with PumpdulerMessage.IMPORT_LOCK:
            if PumpdulerMessage.parser is None:
                parser_path = parser_path or config.MESSAGE_PARSER_CLASS
                module_name, class_name = parser_path.split(":")
                module = importlib.import_module(module_name)
                PumpdulerMessage.parser = getattr(module, class_name)

    @staticmethod
    def dump(data: typing.Any):
        PumpdulerMessage.setup()
        message = PumpdulerMessage.parser.encode(data)
        if isinstance(message, bytes) is True:
            return message + PumpdulerMessage.MESSAGE_END_SIGN
        raise ValueError(f"{config.MESSAGE_PARSER_CLASS} must return bytes.")

    @staticmethod
    def load(data: typing.Union[str, bytes]):
        PumpdulerMessage.setup()
        if isinstance(data, bytes) is True:
            data = data.decode("utf-8")
        return PumpdulerMessage.parser.decode(data)
