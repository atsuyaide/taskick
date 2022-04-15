import importlib
import itertools
import logging
import re
import subprocess
import threading
import time
from typing import Callable, List, Optional, Union

from schedule import Scheduler
from watchdog.events import FileMovedEvent
from watchdog.observers.polling import PollingObserver as Observer

VERSION_MAJOR = "0"
VERSION_MINOR = "1"
VERSION_BUILD = "5"
VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD)
VERSION_STRING = "%s.%s.%s" % VERSION_INFO

__version__ = VERSION_STRING

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


def set_a_task_to_scheduler(
    scheduler: Scheduler, crontab_format: str, task: Callable, *args, **kwargs
) -> Scheduler:
    """Register a task to the Scheduler.

    Args:
        scheduler (Scheduler): _description_
        crontab_format (str): Only the **simplified** Crontab format can be processed.
        task (Callable): Tasks to be registered. If you want to pass arguments, use *args and **kwargs.

    Returns:
        Scheduler: Updated Scheduler.
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
                raise ValueError("Invalid format.")

            cv_list.extend(list(map(str, list(range(s, e, int(interval))))))
        merged_cron_str_list.append(cv_list)

    cron_value_products = list(itertools.product(*merged_cron_str_list))
    simple_form_list = sorted([" ".join(x) for x in cron_value_products])
    return simple_form_list


def get_execute_command_list(commands: list, options: dict) -> List[str]:
    if options is None:
        return commands

    for key, value in options.items():
        commands.append(key)
        if value is not None:
            commands.append(f'"{value}"')

    return commands


class CommandExecuter:
    def __init__(
        self, task_name: str, command: str, propagate: bool = False, shell: bool = False
    ) -> None:
        self._task_name = task_name
        self._comand = command
        self._propagate = propagate
        self._shell = shell

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
        logger.debug(event)
        command = self._comand
        if self._propagate:
            event_options = self._get_event_options(event)
            command = get_execute_command_list(command, event_options)

        command = " ".join(command)
        logger.debug(command)
        self.execute(command)

    def execute_by_scheduler(self) -> None:
        self.execute()

    def execute(self, command: str = None) -> None:
        if command is None:
            command = " ".join(self._comand)

        logger.info(f"Executing: {self._task_name}")
        logger.debug(f"Executing detail: {command}")
        return subprocess.Popen(command, shell=self._shell)

    @property
    def task_name(self):
        return self._task_name


class BaseThread(threading.Thread):
    def __init__(self, *pargs, **kwargs):
        super().__init__(daemon=True, *pargs, **kwargs)


class ThreadingScheduler(Scheduler, BaseThread):
    def __init__(self) -> None:
        Scheduler.__init__(self)
        BaseThread.__init__(self)
        self._is_active = True

    def run(self) -> None:
        while self._is_active:
            self.run_pending()
            time.sleep(1)

    def stop(self) -> None:
        self._is_active = False


class SchedulingDetail:
    def __init__(self, detail: dict) -> None:
        self._when = detail["when"]

    @property
    def when(self) -> str:
        return self._when


class ObservingDetail:
    def __init__(self, detail: dict) -> None:
        self._path = detail["path"]
        self._when = detail["when"]
        self._recursive = detail["recursive"]
        self._handler = detail["handler"]
        self._handler_args = detail
        del self._handler_args["handler"]
        del self._handler_args["when"]

    @property
    def when(self) -> str:
        return self._when

    @property
    def recursive(self) -> str:
        return self._recursive

    @property
    def handler(self) -> str:
        return self._handler

    @property
    def handler_args(self):
        return self._handler_args


class BaseExecutionDetail:
    def __init__(self, detail: dict) -> None:
        self._propagate = (
            False if "propagate" not in detail.keys() else detail["propagate"],
        )
        self._event_type = detail["event_type"]
        self._shell = (True if "shell" not in detail.keys() else detail["shell"],)
        self._startup = detail["startup"] if "startup" in detail.keys() else False
        self._await_task = (
            detail["await_task"] if "await_task" in detail.keys() else None
        )

    def is_startup(self) -> bool:
        return self._startup

    def is_propagate(self) -> bool:
        return self._propagate

    def is_shell(self) -> bool:
        return self._shell

    def is_await(self) -> bool:
        return self._await_task is not None

    @property
    def await_task(self) -> str:
        return self._await_task


class TimeExecutionDetail(BaseExecutionDetail):
    def __init__(self, detail: dict) -> None:
        super().__init__(detail)
        self.SD = SchedulingDetail(detail["detail"])

    @property
    def when(self) -> str:
        return self.SD.when


class FileExecutionDetail(BaseExecutionDetail):
    def __init__(self, detail: dict) -> None:
        super().__init__(detail)
        self.OD = ObservingDetail(detail["detail"])

    @property
    def when(self) -> ObservingDetail:
        return self.OD


class NullExecutionDetail(BaseExecutionDetail):
    def __init__(self, detail: dict) -> None:
        super().__init__(detail)
        self._startup = True

    @property
    def when(self) -> str:
        pass


def get_execution_detail(detail: dict) -> BaseExecutionDetail:
    if detail["event_type"] is None:
        return NullExecutionDetail(detail)
    if detail["event_type"] == "time":
        return TimeExecutionDetail(detail)
    if detail["event_type"] == "file":
        return FileExecutionDetail(detail)

    raise ValueError('"{:}" does not defined.'.format(detail["event_type"]))


class TaskDetail:
    def __init__(self, task_name: str, detail: dict) -> None:
        self._ED = get_execution_detail(detail["execution"])
        self._task_name = task_name
        self._commands = detail["commands"]
        self._options = detail["options"] if "options" in detail.keys() else None
        self._is_active = True if detail["status"] == 1 else False

    @property
    def task_name(self) -> str:
        return self._task_name

    @property
    def event_type(self) -> bool:
        return self._ED._event_type

    @property
    def options(self) -> Optional[List[str]]:
        return self._options

    @property
    def commands(self) -> List[str]:
        return self._commands

    @property
    def when_run(self) -> Union[str, List[str]]:
        return self._ED.when

    @property
    def await_task(self) -> str:
        return self._ED.await_task

    @property
    def executor_args(self) -> dict:
        return {
            "task_name": self.task_name,
            "command": get_execute_command_list(self.commands, self.options),
            "propagate": self.is_propagate,
            "shell": self.is_shell,
        }

    def is_active(self) -> bool:
        return self._is_active

    def is_startup(self) -> bool:
        return self._ED.is_startup()

    def is_propagate(self) -> bool:
        return self._ED.is_propagate()

    def is_shell(self) -> bool:
        return self._ED.is_shell()

    def is_await(self) -> bool:
        return self._ED.is_await()


def update_scheduler(
    scheduler: Scheduler, crontab_format: str, task: Callable, *args, **kwargs
) -> Scheduler:
    crontab_format_list = simplify_crontab_format(crontab_format)

    for crontab_format in crontab_format_list:
        scheduler = set_a_task_to_scheduler(
            scheduler, crontab_format, task, *args, **kwargs
        )

    return scheduler


def update_observer(
    observer: Observer, observe_detail: ObservingDetail, task: Callable
) -> Observer:
    handler_detail = observe_detail.handler
    event_type_detail = observe_detail.when

    EventHandlers = importlib.import_module("watchdog.events")

    if "args" in handler_detail.keys():
        handler = getattr(EventHandlers, handler_detail["name"])(
            **handler_detail["args"]
        )
    else:
        handler = getattr(EventHandlers, handler_detail["name"])()

    for event_type in event_type_detail:
        setattr(handler, f"on_{event_type}", task)

    kwargs = observe_detail.handler_args
    kwargs["event_handler"] = handler
    observer.schedule(**kwargs)

    return observer


class TaskRunner:
    def __init__(self) -> None:
        self._scheduler = ThreadingScheduler()
        self._observer = Observer()

        self._startup_execution_tasks = {}
        self._running_startup_tasks = {}
        self._registered_tasks = {}
        self._scheduling_tasks = {}
        self._observing_tasks = {}
        self._await_tasks = {}  # {"A": "B"} -> "A" waits for "B" to finish.

    def register(self, job_config: dict):
        TD_list = [TaskDetail(*params) for params in job_config.items()]
        for TD in TD_list:
            if not TD.is_active():
                logger.info(f"Skipped: {TD.task_name}")
                continue
            if self.is_registered(TD.task_name):
                raise ValueError(f"{TD.task_name} is already exists.")

            logger.info(f"Processing: {TD.task_name}")
            task = CommandExecuter(**TD.executor_args)

            if TD.is_startup():
                logger.info("Startup option is selected.")
                self._startup_execution_tasks[TD.task_name] = task
            if TD.is_await():
                logger.info("Await option is selected.")
                self._await_tasks[TD.task_name] = TD.await_task

            self._register(TD, task)
            self._registered_tasks[TD.task_name] = task
            logger.info("Registered")

        return self

    def _register(self, TD: TaskDetail, task: CommandExecuter) -> None:
        if TD.event_type == "time":
            self._scheduler = update_scheduler(
                self._scheduler,
                TD.when_run,
                task.execute_by_scheduler,
            )
            self._scheduling_tasks[TD.task_name] = task
        if TD.event_type == "file":
            self._observer = update_observer(
                self._observer, TD.when_run, task.execute_by_observer
            )
            self._observing_tasks[TD.task_name] = task

    def _await_running_task(self, task_name) -> None:
        for await_task_name in self._await_tasks[task_name]:
            if await_task_name not in self._running_startup_tasks.keys():
                raise ValueError(f'"{await_task_name}" is not running.')
            logger.info(f'"{task_name}" is waiting for "{await_task_name}" to finish.')
            self._running_startup_tasks[await_task_name].wait()

    def _run_startup_task(self):
        for task_name, task in self._startup_execution_tasks.items():
            if task_name in self._await_tasks.keys():
                self._await_running_task(task_name)
            self._running_startup_tasks[task_name] = task.execute()

    def run(self) -> None:
        """
        Executes registered tasks.
        Scheduled/Observed tasks will not be executed until the startup task is complete.
        """
        self._run_startup_task()
        self._observer.start()
        self._scheduler.start()

    def is_registered(self, task_name: str) -> bool:
        return task_name in self._registered_tasks.keys()

    def stop_startup_task(self):
        for proc in self._running_startup_tasks.values():
            proc.kill()

    def join_startup_task(self):
        for proc in self._running_startup_tasks.values():
            proc.wait()

    def stop(self) -> None:
        """Stop execution of registered tasks other than the startup task."""
        self.stop_startup_task()
        self._observer.stop()
        self._scheduler.stop()

    def join(self) -> None:
        self.join_startup_task()
        self._observer.join()
        self._scheduler.join()

    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        pass

    @property
    def scheduling_tasks(self):
        return self._scheduling_tasks

    @property
    def observing_tasks(self):
        return self._observing_tasks

    @property
    def tasks(self) -> dict:
        return self._registered_tasks

    @property
    def startup_tasks(self) -> dict:
        return self._startup_execution_tasks
