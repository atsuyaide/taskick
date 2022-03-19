__version__ = "0.1.3"


import importlib
import itertools
import logging
import re
import subprocess
import time
from typing import Callable, List, Tuple

from schedule import Scheduler
from watchdog.events import FileMovedEvent
from watchdog.observers.polling import PollingObserver as Observer

logger = logging.getLogger("taskick")


WEEKS = [
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
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


def set_scheduled_job(scheduler: Scheduler, crontab_format: str, task: Callable, *args, **kwargs) -> Scheduler:
    """_summary_

    Args:
        scheduler (Scheduler): _description_
        crontab_format (str): _description_
        task (Callable): _description_

    Raises:
        ValueError: _description_

    Returns:
        Scheduler: _description_
    """
    if re.match("^( *(\\*|\\d+|(\\*|\\d+)/(\\*|\\d+))){5} *$", crontab_format) is None:
        raise ValueError("Invalid foramt.")

    if re.match("^( *\\*){5} *$", crontab_format):
        crontab_format = "*/1 * * * *"

    if "/" in crontab_format:
        time_values = crontab_format.split("/")[0]
    else:
        time_values = crontab_format

    time_values = time_values.split()[:-1][::-1]
    time_values = [x.zfill(2) for x in time_values]

    if len(time_values) == 0:
        hh, mm, ss = "00", "00", "00"
    elif len(time_values) == 1:
        hh, mm, ss = "00", time_values[0], "00"
    elif len(time_values) == 2:
        hh, mm, ss = time_values[0], time_values[1], "00"
    elif len(time_values) == 3:
        hh, mm, ss = "00", time_values[1], time_values[2]
    elif len(time_values) == 4:
        hh, mm, ss = time_values[2], time_values[3], "00"

    every = 1
    every_method_is_called = False
    unit = None
    unit_method_is_called = False

    cron_values = crontab_format.split()[::-1]
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
                    every = int(unit_str.split("/")[-1])
                    unit = UNITS[i]
                elif unit is None:
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

    # - For daily jobs -> `HH:MM:SS` or `HH:MM`
    # - For hourly jobs -> `MM:SS` or `:MM`
    # - For minute jobs -> `:SS`
    if "day" in unit:
        at_time = f"{hh}:{mm}:{ss}"
    elif "hour" in unit:
        at_time = f"{mm}:{ss}"
    elif "minute" in unit:
        at_time = f":{ss}"

    at_time = at_time.replace("0*", "00")
    job = job.at(at_time)

    job.do(task, *args, **kwargs)
    logger.debug(f"Added: {repr(job)}")
    return scheduler


def simplify_crontab_format(crontab_format: str) -> List[str]:
    """_summary_

    Args:
        crontab_format (str): _description_

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        List[str]: _description_
    """
    cron_values = crontab_format.split()

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
                e = UNITS_UPPER[UNITS[-i - 1]]
            elif re.match("^\\d+-\\d+/\\d+$", unit_str):
                unit_str, interval = unit_str.split("/")
                s, e = map(int, unit_str.split("-"))
                e += 1
            else:
                raise ValueError

            cv_list.extend(list(map(str, list(range(s, e, int(interval))))))
        merged_cron_str_list.append(cv_list)

    cron_value_products = list(itertools.product(*merged_cron_str_list))
    simple_form_list = sorted([" ".join(x) for x in cron_value_products])
    return simple_form_list


def update_scheduler(scheduler: Scheduler, crontab_format: str, task: Callable, *args, **kwargs) -> Scheduler:
    """_summary_

    Args:
        scheduler (Scheduler): _description_
        crontab_format (str): _description_
        task (Callable): _description_

    Returns:
        Scheduler: _description_
    """
    crontab_format_list = simplify_crontab_format(crontab_format)

    for crontab_format in crontab_format_list:
        scheduler = set_scheduled_job(scheduler, crontab_format, task, *args, **kwargs)

    return scheduler


def update_observer(observer: Observer, observe_detail: dict, task: Callable) -> Observer:
    """_summary_

    Args:
        observer (Observer): _description_
        observe_detail (dict): _description_
        task (Callable): _description_

    Returns:
        Observer: _description_
    """

    handler_detail = observe_detail["handler"]
    event_type_detail = observe_detail["when"]

    EventHandlers = importlib.import_module("watchdog.events")

    if "args" in handler_detail.keys():
        handler = getattr(EventHandlers, handler_detail["name"])(**handler_detail["args"])
    else:
        handler = getattr(EventHandlers, handler_detail["name"])()

    for event_type in event_type_detail:
        setattr(handler, f"on_{event_type}", task)

    del observe_detail["handler"]
    del observe_detail["when"]
    observe_detail["event_handler"] = handler

    observer.schedule(**observe_detail)
    return observer


def get_execution_commands(commands: list, options: dict) -> List[str]:
    """_summary_

    Args:
        commands (list): _description_
        options (dict): _description_

    Returns:
        List[str]: _description_
    """
    if options is None:
        return commands

    for key, value in options.items():
        commands.append(key)
        if value is not None:
            commands.append(f'"{value}"')

    return commands


class CommandExecuter:
    """_summary_"""

    def __init__(self, task_name: str, command: str, propagate: bool = False) -> None:
        """_summary_

        Args:
            commands (List[str]): _description_
        """
        self.task_name = task_name
        self.command = command
        self.propagate = propagate

    def _get_event_options(self, event) -> dict:
        if isinstance(event, FileMovedEvent):
            event_keys = ["--event_type", "--src_path", "--dest_path", "--is_directory"]
            event_values = event.key
        else:
            event_keys = ["--event_type", "--src_path", "--is_directory"]
            event_values = event.key

        event_options = dict(zip(event_keys, event_values))

        if event_options["--is_directory"]:
            event_options["--is_directory"] = None
        else:
            del event_options["--is_directory"]

        return event_options

    def execute_by_observer(self, event) -> None:
        """_summary_

        Args:
            event (_type_): _description_
        """
        logger.debug(event)
        command = self.command
        if self.propagate:
            event_options = self._get_event_options(event)
            command = get_execution_commands(command, event_options)

        command = " ".join(command)
        logger.debug(command)
        self.execute(command)

    def execute_by_scheduler(self) -> None:
        """_summary_"""
        self.execute()

    def execute(self, command: str = None) -> None:
        if command is None:
            command = " ".join(self.command)

        logger.info(f"Executing: {self.task_name}")
        logger.debug(f"Detail: {command}")
        subprocess.Popen(command, shell=True)


def load_and_setup(config: dict) -> Tuple[Scheduler, Observer, List[CommandExecuter]]:
    """_summary_

    Args:
        config (dict): _description_

    Raises:
        ValueError: _description_

    Returns:
        Tuple[Scheduler, Observer, List[CommandExecuter]]: _description_
    """
    scheduler = Scheduler()
    observer = Observer()
    immediate_execution_CE: List[CommandExecuter] = []
    for task_name, task_detail in config.items():
        logger.debug(task_detail)
        if task_detail["status"] != 1:
            logger.info(f"Skipped: {task_name}")
            continue
        else:
            logger.info(f"Processing: {task_name}")

        commands = task_detail["commands"]
        execution_detail = task_detail["execution"]

        if "options" in task_detail.keys():
            options = task_detail["options"]
        else:
            options = None

        commands = get_execution_commands(commands, options)

        if execution_detail["event_type"] is None:
            CE = CommandExecuter(task_name, commands)
            execution_detail["immediate"] = True
        elif execution_detail["event_type"] == "time":
            CE = CommandExecuter(task_name, commands)
            schedule_detail = execution_detail["detail"]
            scheduler = update_scheduler(scheduler, schedule_detail["when"], CE.execute_by_scheduler)
        elif execution_detail["event_type"] == "file":
            if "propagate" not in execution_detail.keys():
                execution_detail["propagate"] = False

            CE = CommandExecuter(task_name, commands, execution_detail["propagate"])
            observe_detail = execution_detail["detail"]
            observer = update_observer(observer, observe_detail, CE.execute_by_observer)
        else:
            raise ValueError("'{:}' is not defined.".format(execution_detail["event_type"]))

        if execution_detail["immediate"]:
            logger.info("Immediate execution option is selected.")
            immediate_execution_CE.append(CE)

    return scheduler, observer, immediate_execution_CE


class TaskRunner:
    """_summary_"""

    def __init__(self, job_config: dict) -> None:
        """_summary_

        Args:
            job_config (dict): _description_

        Raises:
            ValueError: _description_
        """
        self.scheduler, self.observer, self.immediate_execution_CE = load_and_setup(job_config)

    def run(self) -> None:
        """_summary_"""
        for CE in self.immediate_execution_CE:
            CE.execute()

        self.observer.start()

        try:
            while True:
                self.scheduler.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.debug("Ctrl-C detected.")
        except Exception as e:
            import traceback

            logger.error(e)
            traceback.print_exc()
        finally:
            self.observer.stop()
            self.observer.join()
