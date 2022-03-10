import pytest
from procman import __version__, set_schedule


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.parametrize(
    ("crontab_fmt", "expected_unit", "expected_time"),
    [
        # schedule.every(1).minute
        ("*/1  *    *    *   *", "hours", None),
        # schedule.every(1).hour
        ("*    */1  *    *   *", "hours", None),
        # schedule.every(1).day
        ("*    *    */1  *   *", "days", None),
        # schedule.every(1).minute.at(":00")
        # ("0    *    *    *   *", "houras", ":00"),
        # # schedule.every(1).hour.at("00:00")
        # ("0    0    *    *   *", "days"),
        # # schedule.every(1).sunday.at("00:00")
        # ("0    0    *    *   0", "weeks"),
    ]
)
def test_set_scheduleule(crontab_fmt, expected_unit, expected_time):
    scheduler = set_schedule(crontab_fmt, print)
    assert scheduler.unit == expected_unit
    assert scheduler.at_time == expected_time


def test_get_obeserver():
    pass
