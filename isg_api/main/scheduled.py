from isg_api.globals import bg_scheduler
import apscheduler.schedulers.base as apsbase


def test_job():
    print('I am working...')


def start_schedule():
    # TODO extend: Every 10 minutes ask for sensor values => store into DB!
    bg_scheduler.add_job(test_job, 'interval', seconds=5)
    if bg_scheduler.state != apsbase.STATE_RUNNING:
        bg_scheduler.start()
