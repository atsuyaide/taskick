__version__ = "0.1.0"


import re
import time
import yaml
import logging
import schedule
import itertools
import subprocess
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

UNITS_UPPER = {
    "week": 7,
    "month": 12,
    "day": 31,
    "hour": 23,
    "minute": 59,
}


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
    logger.debug(f"Job has been added: {repr(job)}")
    return scheduler


def simplify_crontab_format(crontab_format: str) -> List[str]:
    cron_values = crontab_format.split()
    if len(cron_values) != 5:
        raise CrontabFormatError('Must consist of five elements.')

    cron_values = [x.split(",") for x in cron_values]

    merged_cron_str_list = []

    for i, unit_str_list in enumerate(cron_values):
        cv_list = []
        for unit_str in unit_str_list:
            interval = 1

            if re.match("^(\\d+|\\*)$", unit_str) or re.match("^\\*/\\d+$", unit_str):
                cv_list.extend([unit_str])
                continue
            elif re.match("^\\d+-\\d+$", unit_str):
                s, e = map(int, unit_str.split("-"))
                e += 1
            elif re.match("^\\d+/\\d+", unit_str):
                s, interval = unit_str.split("/")
                s = 0 if s == "*" else int(s)
                e = UNITS_UPPER[UNITS[-i-1]]
            elif re.match("^\\d+-\\d+/\\d+$", unit_str):
                unit_str, interval = unit_str.split("/")
                s, e = map(int, unit_str.split("-"))
                e += 1
            else:
                raise CrontabFormatError

            cv_list.extend(list(map(str, list(range(s, e, int(interval))))))
        merged_cron_str_list.append(cv_list)

    cron_value_products = list(itertools.product(*merged_cron_str_list))
    simple_form_list = sorted([" ".join(x) for x in cron_value_products])
    # logger.debug(f"Add schedule: {simple_form_list}")
    return simple_form_list


def update_scheduler(scheduler: schedule.Scheduler, crontab_format: str, task: Callable, *args, **kwargs) -> schedule.Scheduler:
    crontab_format_list = simplify_crontab_format(crontab_format)

    for crontab_format in crontab_format_list:
        scheduler = set_scheduled_job(
            scheduler, crontab_format, task, *args, **kwargs)

    return scheduler


def get_observer(folder_path: str, event_type: str):
    pass


class TaskRunner:
    def __init__(self, job_config: str) -> None:
        self.scheduler = schedule.Scheduler()
        self.observer = None

        with open(job_config, "r") as f:
            config = yaml.safe_load(f)

        for task_name, task_detail in config.items():
            logger.debug(f"{task_name}: {task_detail}")
            if task_detail['status'] != 1:
                logger.debug(f"{task_name} skipped.")
                continue

            script_path = task_detail["script_path"]
            options_detail = task_detail["options"]
            execution_detail = task_detail["execution"]
            cmd = self._get_execution_cmd(script_path, options_detail)

            if execution_detail["immediate"]:
                self._execute_cmd(cmd)

            if execution_detail["event_type"] == "time":
                self.scheduler = update_scheduler(
                    self.scheduler,
                    execution_detail["when"],
                    self._execute_cmd,
                    cmd
                )
            elif execution_detail["event_type"] == "file":
                pass
            else:
                raise ValueError
            logger.info(f"'{task_name}' was Registered.")

    def _get_execution_cmd(self, file_path: str, options: dict) -> str:
        cmd = ["python", file_path]

        for key, value in options.items():
            cmd.append(f"--{key}")
            if value is not None:
                cmd.append(value)

        return cmd

    def _execute_cmd(self, cmd: list) -> None:
        logger.debug('Started: ' + " ".join(cmd))
        subprocess.Popen(cmd)

    def run(self) -> None:
        while True:
            self.scheduler.run_pending()
            time.sleep(1)
