import typing
import threading
from dataclasses import dataclass
from .time_event import TimeEvent
from .functions import get_datetime
from .logger import logger


@dataclass(frozen=True)
class TimeEventExecutorArgs:
    time_event: TimeEvent
    broadcast_func: typing.Callable[[TimeEvent], None]


class TimeEventExecutor(object):
    """
    Executor for the time event, this will start a thread to execute
    the time event, with this executor the event can be skipped or
    can be executed.

    This provides methods to start and skip the execution of the
    time event object.
    """
    def __init__(self, args: TimeEventExecutorArgs) -> None:
        self._args: TimeEventExecutorArgs = args
        self._time_event: TimeEvent = self._args.time_event
        self._wait_event: threading.Event = threading.Event()
        self._is_skipped: bool = False

    @property
    def time_event_id(self) -> str:
        """
        Returns:
            (str) id of the current time event object
        """
        return self._args.time_event.id

    def skip(self):
        """
        Skips the execution of the current time event.
        """
        self._is_skipped = True
        self._wait_event.set()

    def _start(self):
        """
        Start the process and wait for the specific amount of time then checks
        if the execution is skipped then do not execute the time event otherwise
        execute it.
        """
        timeout_time = self._time_event.exec_timestamp - get_datetime().timestamp()
        if timeout_time > 0:
            self._wait_event.wait(timeout=timeout_time)
        if self._is_skipped is True:
            logger.debug(f"TimeEventExecutor skipped: {self.time_event_id}")
            return
        logger.debug("TimeEventExecutor executing:", self.time_event_id)
        self._args.broadcast_func(self._time_event)

    def start(self):
        """
        Starts the thread and also clears the wait event.
        """
        thread = threading.Thread(target=self._start)
        self._wait_event.clear()
        thread.start()
