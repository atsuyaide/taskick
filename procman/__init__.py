__version__ = "0.1.0"


import re
import logging
import schedule
import itertools
from typing import Callable, List

logger = logging.getLogger('procman')


class ProcmanError(Exception):
    """Base Procaman exception"""

    pass


class CrontabFormatError(ProcmanError):
    """An improper crontab format was used"""

    pass


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


def set_scheduled_job(scheduler: schedule.Scheduler, crontab_format: str, task: Callable, *args, **kwargs) -> schedule.Scheduler:
    if re.match("^( *\\*){5} *$", crontab_format):
        return set_scheduled_job(scheduler, "*/1 * * * *", task)

    cron_values = crontab_format.split()[::-1]
    every = 1
    unit_method_is_called = False
    every_method_is_called = False

    if "/" in crontab_format:
        at_time = None
    else:
        time_values = crontab_format.split()[:-1][::-1]
        time_values = list(filter(lambda x: x != "*", time_values))
        time_values = list(map(int, time_values))

        if len(time_values) == 1:
            at_time = ":{:02}".format(time_values[0])
        elif len(time_values) == 2:
            at_time = "{:02}:{:02}:00".format(time_values[0], time_values[1])
        else:
            raise CrontabFormatError("Invalid format.")

        at_time = at_time.replace("*", "")

    for i, unit_str in enumerate(cron_values):
        # print(f"{unit_str} : ", end="")
        if unit_str == "*":
            # print("skipped")
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
            print(repr(scheduler))
            job = scheduler.every(every)
            every_method_is_called = not every_method_is_called

        if not unit_method_is_called:
            if every != 1:
                unit += "s"
            # print(unit)
            job = getattr(job, unit)
            unit_method_is_called = not unit_method_is_called

    if at_time is not None:
        # print(at_time)
        job = job.at(at_time)

    job.do(task, *args, **kwargs)
    logger.debug(repr(scheduler))
    print(repr(scheduler))
    return scheduler


def split_crontab_format_simple_form(crontab_format: str) -> List[str]:
    cron_values = crontab_format.split()
    cron_values = [x.split(",") for x in cron_values]
    temp_cron_values = []

    for x in cron_values:
        u = []
        for y in x:
            interval = 1
            if re.match("^\\d+$", y):
                u.extend(y)
                continue
            elif re.match("^\\*$", y):
                pass
            elif re.match("^\\*$/\\d+", y):
                pass
            elif re.match("^(\\*|\\d+|\\d+-\\d+|)/\\d+$", y):
                y, interval = y.split("/")

            if re.match("^\\d+-\\d+$", y):
                s, e = map(int, y.split("-"))
                y = list(map(str, list(range(s, e + 1, int(interval)))))

            u.extend(y)
        # print(u)
        temp_cron_values.append(u)
    cron_values = temp_cron_values
    # print(cron_values)

    if len(cron_values) != 5:
        raise CrontabFormatError('Must consist of five elements.')

    cron_value_products = list(itertools.product(*cron_values))
    simple_form = sorted([" ".join(x) for x in cron_value_products])
    print(simple_form)
    return simple_form


def get_scheduler(crontab_format: str, task: Callable) -> schedule.Scheduler:
    scheduler = schedule.Scheduler()
    crontab_format_list = split_crontab_format_simple_form(crontab_format)

    for crontab_format in crontab_format_list:
        scheduler = set_scheduled_job(scheduler, crontab_format, task)

    return scheduler


def get_observer(folder_path: str, event_type: str):
    pass


class Procaman(object):
    def __init__(self) -> None:
        super().__init__()

    def run() -> None:
        pass
