def check_job_properties(expected_job, job):
    assert expected_job.interval == job.interval
    assert expected_job.latest == job.latest
    assert expected_job.unit == job.unit
    assert expected_job.at_time == job.at_time
    assert expected_job.last_run == job.last_run
    assert expected_job.period == job.period
    assert expected_job.start_day == job.start_day
    assert expected_job.cancel_after == job.cancel_after
    assert expected_job.tags == job.tags
