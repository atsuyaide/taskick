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


def set_schedule(crontab_fmt: str, task: Callable, *args, **kwargs) -> schedule.Scheduler:
    scheduler = schedule.Scheduler()
    every = 1
    interval_is_uncall = True
    for i, unit in enumerate(crontab_fmt.split()[::-1]):
        print(f"[{i}] {unit}: ", end="")
        if unit == "*":
            print(f"skipped {UNITS[i]}")
            continue
        else:
            if re.match("^\\*/\\d+$", unit):
                every = int(unit.split('/')[-1])

            if interval_is_uncall:
                scheduler = scheduler.every(every)
                interval_is_uncall = False

            print(UNITS[i])
            scheduler = getattr(scheduler, UNITS[i])
    scheduler = scheduler.do(task, *args, **kwargs)
    logger.debug(repr(scheduler))
    print(scheduler.at_time)
    return scheduler


def get_observer(folder_path: str, event_type: str):
    pass


class Procaman(object):
    def __init__(self) -> None:
        super().__init__()

    def run() -> None:
        pass
