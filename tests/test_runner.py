import os

import pytest
import schedule
import yaml
from taskick.runner import TaskRunner, update_scheduler

from .utils import check_job_properties


@pytest.mark.parametrize(
    ("crontab_format", "expected_job_list"),
    [
        (
            "*       *   *   *   *",
            [
                schedule.every(1).minute.at(":00").do(print),
            ],
        ),
        (
            "1       *   *   *   *",
            [
                schedule.every(1).hour.at(":01").do(print),
            ],
        ),
        (
            "0,1     *   *   *   *",
            [
                schedule.every(1).hour.at(":00").do(print),
                schedule.every(1).hour.at(":01").do(print),
            ],
        ),
        (
            "0-2      *   *   *   *",
            [
                schedule.every(1).hour.at(":00").do(print),
                schedule.every(1).hour.at(":01").do(print),
                schedule.every(1).hour.at(":02").do(print),
            ],
        ),
        (
            "1-7/2    *   *   *   *",
            [
                schedule.every(1).hour.at(":01").do(print),
                schedule.every(1).hour.at(":03").do(print),
                schedule.every(1).hour.at(":05").do(print),
                schedule.every(1).hour.at(":07").do(print),
            ],
        ),
        (
            "0,1-7/2 *   *   *   *",
            [
                schedule.every(1).hour.at(":00").do(print),
                schedule.every(1).hour.at(":01").do(print),
                schedule.every(1).hour.at(":03").do(print),
                schedule.every(1).hour.at(":05").do(print),
                schedule.every(1).hour.at(":07").do(print),
            ],
        ),
    ],
)
def test_update_scheduler(crontab_format, expected_job_list):
    scheduler = schedule.Scheduler()
    scheduler = update_scheduler(scheduler, crontab_format, print)
    assert len(scheduler.jobs) == len(expected_job_list)
    for expected_job, job in zip(expected_job_list, scheduler.jobs):
        check_job_properties(expected_job, job)


def test_update_observer():
    pass


def test_command_executer():
    pass


@pytest.mark.parametrize(
    (
        "file_name",
        "expected_task_count",
        "expected_startup_task_count",
        "expected_scheduling_task_count",
        "expected_observing_task_count",
    ),
    [
        ("config/empty.yaml", 0, 0, 0, 0),
        ("config/vanilla.yaml", 1, 1, 0, 0),
        ("config/time_trigger.yaml", 2, 1, 2, 0),
        ("config/file_trigger.yaml", 3, 0, 0, 3),
        ("config/await.yaml", 3, 3, 0, 0),
    ],
)
def test_taskrunner_register(
    file_name,
    expected_task_count,
    expected_startup_task_count,
    expected_scheduling_task_count,
    expected_observing_task_count,
):
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(test_dir, file_name), "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    TR = TaskRunner()
    TR.register(config)
    assert len(TR.tasks) == expected_task_count
    assert len(TR.startup_tasks) == expected_startup_task_count
    assert len(TR.scheduling_tasks) == expected_scheduling_task_count
    assert len(TR.observing_tasks) == expected_observing_task_count


@pytest.mark.parametrize(
    ("task_name", "expected_exception"),
    [
        ("invalid_event_type", ValueError),
        ("invalid_crontab_format", ValueError),
        ("invalid_event_handler", AttributeError),
        ("invalid_event_type_of_watchdog", AttributeError),
    ],
)
def test_invalid_registration(task_name, expected_exception):
    test_path = os.path.join(os.path.dirname(__file__), "config/invalid.yaml")
    with open(test_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    invalid_config = {task_name: config[task_name]}
    TR = TaskRunner()
    with pytest.raises(expected_exception):
        TR.register(invalid_config)


def test_run():
    pass
