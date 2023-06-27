from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from isg_api.sensors.temperature.temperature import SenseTemperature
from isg_api.globals import scheduler, db
from isg_api.comm.ble.smart_leaf import BleSmartLeaf
from isg_api.models import SmartLeaf, SensorData
from datetime import datetime

import isg_api.globals_smart_leafs as smd
import asyncio

loop_running = False
@scheduler.task('cron', id='ble_heartbeat', minute='*')
def ble_heartbeat():
    global loop_running
    asyncio.set_event_loop(smd.loop)

    print('Starting cron job "ble-heartbeat"')

    if smd.ble_smart_leafs is None or len(smd.ble_smart_leafs) == 0:
        # First get all the BLE-device addresses from the DB
        print('need to create new objects...')
        with scheduler.app.app_context():
            macs = db.session.query(SmartLeaf.mac_address).all()
            macs = [mac for mac, in macs]  # Unpacking the tuple

        # Then try to connect to every BLE-device
        for mac in macs:
            smd.ble_smart_leafs.append(BleSmartLeaf(mac))

    if not loop_running:
        def run_forever(loop):
            loop.run_forever()

        thread = Thread(target=run_forever, args=(smd.loop,))
        thread.start()

        loop_running = True

    with ThreadPoolExecutor() as executor:
        try:
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(executor, asyncio.wait_for, simple_connect(c), 150) for c in smd.ble_smart_leafs]
            completed, pending = loop.run_until_complete(asyncio.wait(tasks))
            for task in completed:
                try:
                    result = task.result() # get the result of completed task
                except Exception as e:
                    print(f"A task completed with an error: {e}")
        except Exception as e:
            print('Exited tasks execution because of an error')
            print(e)


def simple_connect(client: BleSmartLeaf):
    client.connect()


@scheduler.task('cron', id='fetch_smart_leaf_report', minute='*/10')
def fetch_smart_leaf_report_cron():
    print('Starting cron job "fetch_smart_leaf_report"')
    if smd.ble_smart_leafs is None or len(smd.ble_smart_leafs) == 0:
        return # no heartbeat yet

        # Initialize the sensor
    sense_temp = SenseTemperature(1, 0x44, 0x2C, [0x06])
    c_temp, f_temp, humidity = sense_temp.read()

    # call the function to write temperature to db here
    with scheduler.app.app_context():
        new_data = SensorData(
            sensor_type_id=3,
            value=c_temp,
            smart_leaf_id=1,
            measured_on=datetime.utcnow()
        )

        db.session.add(new_data)
        db.session.commit()

    smd.loop.call_soon_threadsafe(
        lambda: asyncio.gather(*(asyncio.wait_for(fetch_smart_leaf_report(c), timeout=50) for c in smd.ble_smart_leafs)))


async def fetch_smart_leaf_report(client: BleSmartLeaf):
    client.set_safe_sensor_values_to_db_mode(True)
    client.send_report_command()
    client.set_safe_sensor_values_to_db_mode(False)


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
