from dataclasses import dataclass


@dataclass(frozen=True)
class TimeEvent:
    """
    Contains details about the event that will be executed.
    """
    id: str     # id of the time event
    channel: str      # channel name to publish in
    exec_timestamp: float   # execution time stamp
    data: str   # data to be sent
    timestamp: float    # timestamp at the time of added
