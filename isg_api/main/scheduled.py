from isg_api.globals import scheduler, db
from isg_api.comm.ble.smart_leaf import BleSmartLeaf
from isg_api.models import SmartLeaf

import asyncio


# run job every 10 minutes
@scheduler.task('cron', id='fetch_smart_leaf_report', minute='*/10')
def connect_to_leafs():
    print('Starting cron job "fetch_smart_leaf_report"')

    # First get all the BLE-device addresses from the DB
    with scheduler.app.app_context():
        macs = db.session.query(SmartLeaf.mac_address).all()
        macs = [mac for mac, in macs] # I honestly don't know why this is needed

    # Then try to connect to every BLE-device
    clients = [BleSmartLeaf(mac) for mac in macs]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.gather(*(fetch_smart_leaf_report(c) for c in clients)))


async def fetch_smart_leaf_report(client: BleSmartLeaf):
    await client.connect()
    await asyncio.sleep(3)

    # Test Report Command - should send back sensor values to notifier.py callbacks
    await client.send_report_command()
    await asyncio.sleep(25)
    await client.disconnect()


async def test_conn(client: BleSmartLeaf):
    await client.connect()
    await asyncio.sleep(3)

    # Test Report Command - should send back sensor values to notifier.py callbacks
    await client.send_report_command()
    await asyncio.sleep(10)

    # Test LED-Range
    for i in range(8):
        await client.send_set_neo_command([i], 255, 0, 0)
        await asyncio.sleep(0.3)

    # reset all LEDs
    await asyncio.sleep(3)
    await client.send_set_neo_clear_all()

    # Test LED-Range without reset
    for i in range(8):
        await client.send_set_neo_command([i], 255, 0, 0, False)
        await asyncio.sleep(0.3)

    # reset all LEDs
    await asyncio.sleep(3)
    await client.send_set_neo_clear_all()

    await client.disconnect()
