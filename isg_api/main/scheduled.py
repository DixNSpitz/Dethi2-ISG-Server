from threading import Thread

from isg_api.globals import scheduler, db
from isg_api.comm.ble.smart_leaf import BleSmartLeaf
from isg_api.models import SmartLeaf
import isg_api.globals_smart_leafs as smd

import asyncio

loop_running = False
@scheduler.task('cron', id='ble_hearbeat', minute='*')
def initialize_smart_leafs():
    global loop_running
    asyncio.set_event_loop(smd.loop)

    print('Starting cron job "ble-heartbeat"')
    if smd.ble_smart_leafs is None or len(smd.ble_smart_leafs) == 0:
        # First get all the BLE-device addresses from the DB
        print('need to create new objects...')
        with scheduler.app.app_context():
            macs = db.session.query(SmartLeaf.mac_address).all()
            macs = [mac for mac, in macs]  # I honestly don't know why this is needed

        # Then try to connect to every BLE-device
        for mac in macs:
            smd.ble_smart_leafs.append(BleSmartLeaf(mac))

    smd.loop.call_soon_threadsafe(lambda: asyncio.gather(*(asyncio.wait_for(simple_connect(c), timeout=50) for c in smd.ble_smart_leafs)))
    #for c in smd.ble_smart_leafs:
        #smd.loop.call_soon_threadsafe(lambda: smd.loop.create_task(asyncio.wait_for(simple_connect(c), timeout=50)))

    try:
        # Run loop forever, but in another Thread, so the current one will be unblocked, which is needed
        # because it is a cron-job!
        def run_forever(loop):
            loop.run_forever()

        # because run_forever() will block the current thread, we spawn
        # a subthread to issue that call in.
        if not loop_running:
            thread = Thread(target=run_forever, args=(smd.loop,))
            thread.start()

            loop_running = True

    except Exception as e:
        print('Exited tasks execution because of timeout')
        print(e)


async def simple_connect(client: BleSmartLeaf):
    client.connect()


# @scheduler.task('cron', id='fetch_smart_leaf_report', minute='*/10') TODO make this work
def connect_to_leafs():
    print('Starting cron job "fetch_smart_leaf_report"')
    if smd.ble_smart_leafs is None or len(smd.ble_smart_leafs) == 0:
        return # no heartbeat yet

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = asyncio.gather(*(asyncio.wait_for(fetch_smart_leaf_report(c), timeout=100) for c in smd.ble_smart_leafs))
    try:
        loop.run_until_complete(tasks)
    except Exception as e:
        print('Exited tasks execution because of timeout')
        print(e)


async def fetch_smart_leaf_report(client: BleSmartLeaf):
    client.set_idle_mode(False)
    client.connect()
    await asyncio.sleep(1)

    # Test Report Command - should send back sensor values to notifier.py callbacks
    client.send_report_command()
    client.set_idle_mode(True)


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
