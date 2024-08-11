# Pumpduler: receive messages on a specific time over sockets

Pumpduler provides functionality to set a message to be sent on specific time.

Pumpduler server must be running in background to receive the messages, this package also contains a connector which can be used to set the time events (this message will be sent on specific time in a specific channel), this message can only be received by the subscribers within a channel.

Run the Pumpduler server
```bash
$ python -m pumpduler
```

Configuration can be changed by modifying the config.py inside the pumpduler directory.

Here's the details about the variables:
- `HOST`, `PORT`: server address to bind.
- `UNIX_SOCKET_PATH`: If you want to use socket file.
- `READ_SIZE`: Read size for the client connections.
- `MAX_CLIENTS`: maximum number of clients.
- `MESSAGE_PARSER_CLASS`: a parser class, that transform data to bytes and also converts data to original form from bytes.
- `TIMEZONE`: what timezone should be used.
- `CONSOLE_LOGGING`: should log messages to console or not.
- `LOG_FILE`: path to a file to log messages in that
- `LOG_LEVEL`: level for log messages, only for messages in console, the log file log level is set to DEBUG means file will receive all type of logs.

## Connector example

### Creating a connection

```python
from pumpduler.connector import PumpdulerConnector

connector = PumpdulerConnector('127.0.0.1', 9090)   # connect using host, port
connector = PumpdulerConnector(None, None, 'path_to_sock.sock')   # connect using unix socket file

# printing the server info
print(connector.info())
```

### Adding a time event

```python
from pumpduler.connector import PumpdulerConnector
from pumpduler.functions import get_datetime
from datetime import timedelta


with PumpdulerConnector('127.0.0.1', 9090) as connector:
    connector.add_time_event(
        dt=get_datetime() + timedelta(seconds=30),
        channel_name='c2',
        data={"time_was": str(get_datetime())}
    )
```

### Publishing a message to channel

```python
from pumpduler.connector import PumpdulerConnector

with PumpdulerConnector('127.0.0.1', 9090) as connector:
    for i in range(10):
        # publishing a message and the channel is "c2"
        connector.publish("c2", {"status": f"working fine {i}!"})
```

### Listening to messages
```python
from pumpduler.connector import PumpdulerConnector

connector = PumpdulerConnector('127.0.0.1', 9090)
connector.subscribe("c2")   # subscribe to channel "c2"
for message in connector.listen():  # start listening for messages
    print(message)
```

*You need to install `pytz` if you want to use another timezone, to run the default package there's no requirement to install anything. Pumpduler mainly relies on built-in modules `sockets`, `threading` and other modules such as `uuid`, `datetime` and etc.*
