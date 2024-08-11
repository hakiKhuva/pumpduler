import typing
import threading
import uuid
from .constants import SeverToClientMessageTypes
from .time_event import TimeEvent
from .functions import get_datetime
from .time_event_executor import TimeEventExecutor, TimeEventExecutorArgs
from .logger import logger

if typing.TYPE_CHECKING:
    from .client_manager import ClientManager


class TimeEventManager(object):
    """
    Manages the time events, this decides what time event should be
    executed first and has methods to add events.
    """
    def __init__(self, client_manager: 'ClientManager') -> None:
        self._time_events: typing.List[TimeEvent] = []   # time event objects
        self._lock: threading.Lock = threading.Lock()   # lock for the time events
        self._executor_lock: threading.Lock = threading.Lock()  # lock to manage the executor
        self._executor: TimeEventExecutor = None    # current executor, this executor holds a time event to execute it.
        self._client_manager: 'ClientManager' = client_manager  # ref to client manager

    def time_events_count(self) -> int:
        """
        Returns:
            (int) number of the time events this manager holds
        """
        return len(self)

    def _update_executor(self):
        """
        Updates the executor and sets the time event to be executed to
        the executor and starts it.

        This will skip the last executor when the new time event execution
        time is less than the current one, this will compare the id of the
        time event objects from the list of all time events and from the
        time event executor, if they're different then the current executor
        will skip the execution and new executor will be created to execute
        the time event.
        """
        logger.debug("Updating time event executor")
        with self._executor_lock:
            # get the current event
            current_time_event = self.get_event()
            # check if there's executor already or not
            if self._executor is not None:
                if current_time_event is not None:  # if has the time event
                    # compare the ids to check time events are same or not
                    if self._executor.time_event_id == current_time_event.id:
                        logger.debug("Executor is not updated as its the same as was before!")
                        return  # no need to update the executor if the ids are same.
                logger.debug(f"Skipping the current executor with id:{self._executor.time_event_id}")
                self._executor.skip()   # tell the executor to skip the job as new time event is arrived.

            if current_time_event is not None:
                logger.debug(f"Adding time event [id:{current_time_event.id}] to the executor")
                args = TimeEventExecutorArgs(
                    time_event=current_time_event,
                    broadcast_func=self._broadcast
                )
                self._executor = TimeEventExecutor(args=args)
                self._executor.start()  # starting new time event executor
                logger.debug(f"New executor started for the id:{current_time_event.id}")

    def add_event(self, channel: str, data: typing.Any, exec_dt: float):
        """
        Add an event to the list of the time events, this also adjust the
        executor to execute the time event.

        Args:
            channel (str): name of then channel
            data (Any): data that can be parsed and encoded by parser
            exec_dt (float): execution timestamp

        Returns:
            (None)
        """
        logger.info("Event received to be added!")
        with self._lock:
            time_event = TimeEvent(
                id=uuid.uuid4().hex,
                channel=channel,
                exec_timestamp=exec_dt,
                data=data,
                timestamp=get_datetime().timestamp()
            )
            self._time_events.append(time_event)
            logger.debug(f"Event:{time_event.id} is added to the time events")
            # sort the time events using execution timestamp
            self._time_events.sort(key=lambda event: event.exec_timestamp)
            self._update_executor() # update the executor

    def get_event(self):
        """
        Returns:
            (pumpduler.time_event.TimeEvent) the top event, the event at 0th index.
        """
        if len(self._time_events) > 0:
            return self._time_events[0]

    def _broadcast(self, time_event: TimeEvent):
        """
        Send the message to the channel, uses client manager method to send
        it to the channel, this will also check for the time event id to
        ensure this should be executed or not.

        This broadcast will only happen if the time event is at the 0th index
        of the time events list.

        Removes the time event and updates the executor for new time event,
        if any exception occurred while sending the time event then the time
        event won't be removed from the list.

        Args:
            time_event (pumpduler.time_event.TimeEvent): time event object

        Returns:
            (None)
        """
        logger.info("[:TimeEventManager] broadcasting a message!")
        logger.debug(f"[:TimeEventManager] broadcasting a message with id: {time_event.id}")
        with self._lock:
            stored_first_event = self.get_event()
            if stored_first_event is not None:
                if stored_first_event.id == time_event.id:
                    try:
                        message_data = {
                            "id": time_event.id,
                            "channel_name": time_event.channel,
                            "timestamp": time_event.timestamp,
                            "exec_timestamp": time_event.exec_timestamp,
                            "data": time_event.data
                        }
                        self._client_manager.channel_manager.broadcast_message(
                            channel_names=[time_event.channel],
                            message_type=SeverToClientMessageTypes.TIME_EVENT,
                            message_data=message_data
                        )
                    except Exception as e:
                        logger.error(f"Exception in TimeEventManager._broadcast: {e}")
                    else:
                        removed_time_event = self._time_events.pop(0)
                        logger.debug(f"Time event removed at index [0]:[id:{removed_time_event.id}]")
                        self._update_executor()

    def __len__(self):
        return len(self._time_events)
