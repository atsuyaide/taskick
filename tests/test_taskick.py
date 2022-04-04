import logging
import os

import pytest
import schedule
import yaml
from taskick import (
    TaskRunner,
    __version__,
    get_execute_command_list,
    set_a_task_to_scheduler,
    simplify_crontab_format,
    update_scheduler,
)

logger = logging.getLogger("taskick")


def test_version():
    assert __version__ == "0.1.5a5"


def _check_job_properties(expected_job, job):
    assert expected_job.interval == job.interval
    assert expected_job.latest == job.latest
    assert expected_job.unit == job.unit
    assert expected_job.at_time == job.at_time
    assert expected_job.last_run == job.last_run
    assert expected_job.period == job.period
    assert expected_job.start_day == job.start_day
    assert expected_job.cancel_after == job.cancel_after
    assert expected_job.tags == job.tags


@pytest.mark.parametrize(
    ("crontab_format", "expected_job"),
    [
        ("*   *   *   *   *", schedule.every(1).minute.at(":00").do(print)),
        (" *   *   *   *   * ", schedule.every(1).minute.at(":00").do(print)),
        ("*/2 *   *   *   *", schedule.every(2).minutes.at(":00").do(print)),
        ("*   */2 *   *   *", schedule.every(2).hours.at(":00").do(print)),
        ("59  */2 *   *   *", schedule.every(2).hours.at(":59").do(print)),
        ("*   23  */2 *   *", schedule.every(2).days.at("23:00").do(print)),
        ("59  23  */2 *   *", schedule.every(2).days.at("23:59").do(print)),
        # schedule library does not support monthly format
        # ("*    *    *    */2 *", schedule.every(2).month.do(print)),
        ("1   *   *   *   *", schedule.every(1).hour.at(":01").do(print)),
        ("1   2   *   *   *", schedule.every(1).day.at("02:01:00").do(print)),
        # schedule library does not support monthly/yearly format
        # ("1   2   1   *   *", schedule.every(1).month.at("02:01:00").do(print)),
        # ("1   2   1   1   *", schedule.every(1).year.at("02:01:00").do(print)),
        ("1   2   *   *   0", schedule.every(1).sunday.at("02:01:00").do(print)),
        ("1   2   *   *   1", schedule.every(1).monday.at("02:01:00").do(print)),
        ("1   2   *   *   2", schedule.every(1).tuesday.at("02:01:00").do(print)),
        ("1   2   *   *   3", schedule.every(1).wednesday.at("02:01:00").do(print)),
        ("1   2   *   *   4", schedule.every(1).thursday.at("02:01:00").do(print)),
        ("1   2   *   *   5", schedule.every(1).friday.at("02:01:00").do(print)),
        ("1   2   *   *   6", schedule.every(1).saturday.at("02:01:00").do(print)),
        ("1   2   *   *   7", schedule.every(1).sunday.at("02:01:00").do(print)),
    ],
)
def test_set_a_task_to_scheduler(crontab_format, expected_job):
    scheduler = schedule.Scheduler()
    scheduler = set_a_task_to_scheduler(scheduler, crontab_format, print)
    for job in scheduler.jobs:
        _check_job_properties(expected_job, job)


@pytest.mark.parametrize(
    ("crontab_format", "expected_crontab_format_list"),
    [
        ("0,1  *    *    *   *", ["0  *    *    *   *", "1  *    *    *   *"]),
        (
            "1-3  *    *    *   *",
            [
                "1  *    *    *   *",
                "2  *    *    *   *",
                "3  *    *    *   *",
            ],
        ),
        (
            "0,1-3  *    *    *   *",
            [
                "0  *    *    *   *",
                "1  *    *    *   *",
                "2  *    *    *   *",
                "3  *    *    *   *",
            ],
        ),
        (
            "0,1-5/2  *    *    *   *",
            [
                "0  *    *    *   *",
                "1  *    *    *   *",
                "3  *    *    *   *",
                "5  *    *    *   *",
            ],
        ),
        (
            "10,5/20  *    *    *   *",
            [
                "5   *    *    *   *",
                "10  *    *    *   *",
                "25  *    *    *   *",
                "45  *    *    *   *",
            ],
        ),
        (
            "10,*/20  *    *    *   *",
            [
                "*/20   *    *    *   *",
                "10  *    *    *   *",
            ],
        ),
        (
            "0,1  0,1    *    *   *",
            [
                "0  0    *    *   *",
                "0  1    *    *   *",
                "1  0    *    *   *",
                "1  1    *    *   *",
            ],
        ),
        (
            "0-1  0-2    *    *   *",
            [
                "0  0    *    *   *",
                "0  1    *    *   *",
                "0  2    *    *   *",
                "1  0    *    *   *",
                "1  1    *    *   *",
                "1  2    *    *   *",
            ],
        ),
        # ("*/2  */2    *    *   *", [
        #     "*/2 *    *    *   *",
        #     "0   */2  *    *   *",
        # ]),
    ],
)
def test_simplify_crontab_format(crontab_format, expected_crontab_format_list):
    expected_crontab_format_list = sorted(expected_crontab_format_list)
    crontab_format_list = simplify_crontab_format(crontab_format)
    assert len(crontab_format_list) == len(expected_crontab_format_list)

    for expected, result in zip(expected_crontab_format_list, crontab_format_list):
        # Replace wasted spaces.
        expected = " ".join(expected.split())
        assert expected == result


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
        _check_job_properties(expected_job, job)


@pytest.mark.parametrize(
    ("crontab_format", "expected_exception"),
    [
        ("*  * * * * *", ValueError),
        ("a  * * * *", ValueError),
        ("** * * * *", ValueError),
        ("*a * * * *", ValueError),
    ],
)
def test_set_a_task_to_scheduler_given_invalid_input(
    crontab_format, expected_exception
):
    scheduler = schedule.Scheduler()
    with pytest.raises(expected_exception):
        scheduler = set_a_task_to_scheduler(scheduler, crontab_format, print)


def test_update_observer():
    pass


@pytest.mark.parametrize(
    ("commands", "options", "expected_commands"),
    [
        (["a", "b"], {"-c": "d"}, ["a", "b", "-c", '"d"']),
    ],
)
def test_get_execute_command_list(commands, options, expected_commands):
    commands = get_execute_command_list(commands, options)
    assert commands == expected_commands


# def test_load_config_and_setup():
#     with open(os.path.join(DIR_NAME, f"jobconf_{os.name}.yaml"), "r", encoding="utf-8") as f:
#         job_config = yaml.safe_load(f)
#
#     scheduler, observer, task_list_needs_execute_immediately = load_config_and_setup(job_config)
#
#     assert isinstance(scheduler, Scheduler)
#     assert isinstance(observer, PollingObserver)
#     for task in task_list_needs_execute_immediately:
#         assert isinstance(task, CommandExecuter)


@pytest.mark.parametrize(
    (
        "file_name",
        "expected_task_count",
        "expected_startup_task_count",
        "expected_scheduling_task_count",
        "expected_observing_task_count",
    ),
    [
        ("config/vanilla.yaml", 1, 1, 0, 0),
        ("config/time_trigger.yaml", 2, 1, 2, 0),
        ("config/file_trigger.yaml", 3, 0, 0, 3),
        ("config/await.yaml", 3, 3, 0, 0),
    ],
)
def test_register(
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
