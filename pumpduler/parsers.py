import json
import typing


class JSON:
    @staticmethod
    def encode(data: typing.Any) -> bytes:
        return json.dumps(data).encode("utf-8")

    @staticmethod
    def decode(data: typing.Union[str, bytes]) -> typing.Any:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)
