import pytest
import schedule
from procman import __version__, set_schedule


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.parametrize(
    ("crontab_fmt", "expected_scheduler"),
    [
        ("*/1  *    *    *   *", schedule.every(1).minute.do(print)),
        ("*    */1  *    *   *", schedule.every(1).hour.do(print)),
        ("*    *    */1  *   *", schedule.every(1).day.do(print)),
        # schedule library does not support monthly format
        # ("*    *    *    */1 *", schedule.every(1).month.do(print)),
        ("0    *    *    *   *", schedule.every(1).hour.at(":00").do(print)),
        ("0    0    *    *   *", schedule.every(1).day.at("00:00:00").do(print)),
        ("0    0    *    *   0", schedule.every(1).sunday.at("00:00:00").do(print)),
        ("0    0    *    *   1", schedule.every(1).monday.at("00:00:00").do(print)),
        ("0    0    *    *   2", schedule.every(1).tuesday.at("00:00:00").do(print)),
        ("0    0    *    *   3", schedule.every(1).wednesday.at("00:00:00").do(print)),
        ("0    0    *    *   4", schedule.every(1).thursday.at("00:00:00").do(print)),
        ("0    0    *    *   5", schedule.every(1).friday.at("00:00:00").do(print)),
        ("0    0    *    *   6", schedule.every(1).saturday.at("00:00:00").do(print)),
        ("0    0    *    *   7", schedule.every(1).sunday.at("00:00:00").do(print)),
    ]
)
def test_set_scheduler(crontab_fmt, expected_scheduler):
    scheduler = schedule.Scheduler()
    scheduler = set_schedule(scheduler, crontab_fmt, print)

    assert expected_scheduler.interval == scheduler.interval
    assert expected_scheduler.latest == scheduler.latest
    assert expected_scheduler.unit == scheduler.unit
    assert expected_scheduler.at_time == scheduler.at_time
    assert expected_scheduler.last_run == scheduler.last_run
    assert expected_scheduler.period == scheduler.period
    assert expected_scheduler.start_day == scheduler.start_day
    assert expected_scheduler.cancel_after == scheduler.cancel_after
    assert expected_scheduler.tags == scheduler.tags


def test_get_obeserver():
    pass
