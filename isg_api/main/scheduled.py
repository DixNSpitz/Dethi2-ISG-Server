from isg_api.globals import scheduler, db
from isg_api.comm.ble.connector import connect_to_devices
from isg_api.models import SmartLeaf
import asyncio


# TODO extend: Every 10 minutes ask for sensor values => store into DB!
@scheduler.task('cron', id='test_job_1', minute='*')
def connect_to_leafs():
    print('Starting cron job...')

    # First get all the BLE-device addresses from the DB
    with scheduler.app.app_context():
        macs = db.session.query(SmartLeaf.mac_address).all()
        macs = [mac for mac, in macs] # I honestly don't know why this is needed

    # Then try to connect to every BLE-device
    if macs:
        asyncio.run(connect_to_devices(macs))
