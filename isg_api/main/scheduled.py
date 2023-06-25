from isg_api.globals import scheduler, db
from isg_api.comm.ble.connector import connect_to_devices
from isg_api.comm.ble.smart_leaf import BleSmartLeaf
from isg_api.models import SmartLeaf

import asyncio
import time


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
        # asyncio.run(connect_to_devices(macs))
        for mac in macs:
            if mac.endswith('BE'):
                client = BleSmartLeaf(mac)
                asyncio.run(test_conn(client))


async def test_conn(client: BleSmartLeaf):
    await client.connect()
    await asyncio.sleep(3)

    # Test Report Command - should send back sensor values to notifier.py callbacks
    await client.send_report_command()
    await asyncio.sleep(3)

    # Test LED-Range
    for i in range(8):
        await client.send_set_neo_command([i], 255, 0, 0)
        await asyncio.sleep(0.1)

    # reset all LEDs
    await client.send_set_neo_clear_all()
    await asyncio.sleep(3)

    # Test LED-Range without reset
    for i in range(8):
        await client.send_set_neo_command([i], 255, 0, 0, False)
        await asyncio.sleep(0.1)

    # reset all LEDs
    await client.send_set_neo_clear_all()

    await asyncio.sleep(3)
    await client.disconnect()
