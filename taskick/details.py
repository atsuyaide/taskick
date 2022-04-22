from typing import List, Optional, Union

from .utils import get_execute_command_list


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
    def handler_args(self) -> dict:
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
