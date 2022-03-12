__version__ = "0.1.0"


import re
from typing import Callable
import schedule
import logging

logger = logging.getLogger('procman')
logging.basicConfig(level=logging.DEBUG)

EVENT_TYPE_MOVED = "moved"
EVENT_TYPE_DELETED = "deleted"
EVENT_TYPE_CREATED = "created"
EVENT_TYPE_MODIFIED = "modified"
EVENT_TYPE_CLOSED = "closed"

WEEKS = [
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]

UNITS = [
    "week",
    "month",
    "day",
    "hour",
    "minute",
]


def set_schedule(scheduler: schedule.Scheduler, crontab_fmt: str, task: Callable, *args, **kwargs) -> schedule.Scheduler:
    cron_values = crontab_fmt.split()[::-1]
    every = 1
    unit_method_is_called = False
    every_method_is_called = False

    if "/" in crontab_fmt:
        at_time = None
    else:
        time_values = crontab_fmt.split()[:-1][::-1]
        time_values = list(filter(lambda x: x != "*", time_values))
        time_values = list(map(int, time_values))
        if len(time_values) == 1:
            at_time = ":{:02}".format(time_values[0])
        elif len(time_values) == 2:
            at_time = "{:02}:{:02}:00".format(time_values[0], time_values[1])

        at_time = at_time.replace("*", "")

    for i, unit_str in enumerate(cron_values):
        if unit_str == "*":
            continue
        else:
            if i == 0:
                # Run task on a weekly units
                unit = WEEKS[int(unit_str)]
            else:
                # Run task on a monthly/daily/hourly/minutely or specific datetime
                if re.match("^\\*/\\d+$", unit_str):
                    every = int(unit_str.split('/')[-1])
                    unit = UNITS[i]
                else:
                    # In the case of time specification, the time unit is shifted by -1.
                    # Run every 23:59 -> Daily
                    # Run every   :59 -> hourly
                    unit = UNITS[i - 1]

        if not every_method_is_called:
            scheduler = scheduler.every(every)
            every_method_is_called = not every_method_is_called

        if not unit_method_is_called:
            scheduler = getattr(scheduler, unit)
            unit_method_is_called = not unit_method_is_called

    if at_time is not None:
        print(at_time)
        scheduler = scheduler.at(at_time)

    scheduler = scheduler.do(task, *args, **kwargs)
    logger.debug(repr(scheduler))
    return scheduler


def get_observer(folder_path: str, event_type: str):
    pass


class Procaman(object):
    def __init__(self) -> None:
        super().__init__()

    def run() -> None:
        pass
