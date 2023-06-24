from isg_api.globals import bg_scheduler
from isg_api.comm.ble.connector import connect_to_leafs
import apscheduler.schedulers.base as apsbase


def test_job():
    connect_to_leafs()


def start_schedule():
    # TODO extend: Every 10 minutes ask for sensor values => store into DB!
    bg_scheduler.add_job(test_job, 'interval', minutes=1)
    if bg_scheduler.state != apsbase.STATE_RUNNING:
        bg_scheduler.start()
