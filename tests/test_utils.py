import pytest
import schedule
from taskick.utils import (
    get_execute_command_list,
    set_a_task_to_scheduler,
    simplify_crontab_format,
)

from .utils import check_job_properties


@pytest.mark.parametrize(
    ("crontab_format", "expected_job"),
    [
        ("*   *   *   *   *", schedule.every(1).minute.at(":00").do(print)),
        (" *  *   *   *   * ", schedule.every(1).minute.at(":00").do(print)),
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
        check_job_properties(expected_job, job)


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
    ("commands", "options", "expected_commands"),
    [
        (["a", "b"], {"-c": "d"}, ["a", "b", "-c", '"d"']),
    ],
)
def test_get_execute_command_list(commands, options, expected_commands):
    commands = get_execute_command_list(commands, options)
    assert commands == expected_commands
