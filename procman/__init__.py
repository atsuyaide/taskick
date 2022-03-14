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
    """_summary_

    Args:
        scheduler (schedule.Scheduler): _description_
        crontab_format (str): _description_
        task (Callable): _description_

    Raises:
        CrontabFormatError: _description_

    Returns:
        schedule.Scheduler: _description_
    """
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
            every_method_is_called = not every_method_is_called
            job = scheduler.every(every)

        if not unit_method_is_called:
            unit_method_is_called = not unit_method_is_called
            if every != 1:
                unit += "s"
            job = getattr(job, unit)

    if at_time is not None:
        # print(at_time)
        job = job.at(at_time)

    job.do(task, *args, **kwargs)
    logger.debug(f"Added: {repr(job)}")
    return scheduler


def simplify_crontab_format(crontab_format: str) -> List[str]:
    """_summary_

    Args:
        crontab_format (str): _description_

    Raises:
        CrontabFormatError: _description_
        CrontabFormatError: _description_

    Returns:
        List[str]: _description_
    """
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
    return simple_form_list


def update_scheduler(scheduler: schedule.Scheduler, crontab_format: str, task: Callable, *args, **kwargs) -> schedule.Scheduler:
    """_summary_

    Args:
        scheduler (schedule.Scheduler): _description_
        crontab_format (str): _description_
        task (Callable): _description_

    Returns:
        schedule.Scheduler: _description_
    """
    crontab_format_list = simplify_crontab_format(crontab_format)

    for crontab_format in crontab_format_list:
        scheduler = set_scheduled_job(
            scheduler, crontab_format, task, *args, **kwargs)

    return scheduler


def get_observer(folder_path: str, event_type: str):
    pass


class TaskRunner:
    """_summary_
    """

    def __init__(self, job_config: str) -> None:
        """_summary_

        Args:
            job_config (str): _description_

        Raises:
            ValueError: _description_
        """
        self.scheduler = schedule.Scheduler()
        self.observer = None

        with open(job_config, "r", encoding='utf-8') as f:
            config = yaml.safe_load(f)

        for task_name, task_detail in config.items():
            logger.debug(f"Processing: {task_name}: {task_detail}")
            if task_detail['status'] != 1:
                logger.debug(f"Skipped: {task_name}")
                continue

            commands = task_detail["commands"]
            options = task_detail["options"]
            execution_detail = task_detail["execution"]
            cmd = self._get_execution_cmd(commands, options)

            if execution_detail["event_type"] == "time":
                self.scheduler = update_scheduler(
                    self.scheduler,
                    execution_detail["when"],
                    self._execute_job,
                    cmd
                )
            elif execution_detail["event_type"] == "file":
                pass
            else:
                raise ValueError
            logger.info(f"Registered: '{task_name}'")

            if execution_detail["immediate"]:
                logger.info('Immediate execution option is selected.')
                self._execute_job(cmd)

    def _get_execution_cmd(self, commands: list, options: dict) -> List[str]:
        """_summary_

        Args:
            file_path (str): _description_
            options (dict): _description_

        Returns:
            list: _description_
        """
        if options is None:
            return commands

        for key, value in options.items():
            commands.append(key)
            if value is not None:
                commands.append(value)

        return commands

    def _execute_job(self, commands: list) -> None:
        """_summary_

        Args:
            commands (list): _description_
        """
        subprocess.Popen(commands)

    def run(self) -> None:
        """_summary_
        """
        while True:
            self.scheduler.run_pending()
            time.sleep(1)
