from isg_api.globals import scheduler, db
from isg_api.comm.ble.smart_leaf import BleSmartLeaf
from isg_api.models import SmartLeaf
import isg_api.smart_leaf_devices as smd

import asyncio

# sensor_type = 0
# run job every 10 minutes

already_connected = False
@scheduler.task('cron', id='ble_hearbeat', minute='*')
def ble_heartbeat():
    global already_connected
    print('Starting cron job "ble-heartbeat"')
    if already_connected:
        print('But already connected so continue with our lives!')
        # return
    if smd.ble_smart_leafs is None or len(smd.ble_smart_leafs) == 0:
        # First get all the BLE-device addresses from the DB
        print('need to create new objects...')
        with scheduler.app.app_context():
            macs = db.session.query(SmartLeaf.mac_address).all()
            macs = [mac for mac, in macs]  # I honestly don't know why this is needed

        # Then try to connect to every BLE-device
        for mac in macs:
            smd.ble_smart_leafs.append(BleSmartLeaf(mac))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = asyncio.gather(*(asyncio.wait_for(simple_connect(c), timeout=50) for c in smd.ble_smart_leafs))
    try:
        loop.run_until_complete(tasks)
    except Exception as e:
        print('Exited tasks execution because of timeout')
        print(e)
    for c in smd.ble_smart_leafs:
        if c.client.is_connected: already_connected = True

async def simple_connect(client: BleSmartLeaf):
    await client.connect()


@scheduler.task('cron', id='fetch_smart_leaf_report', minute='*/10')
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
    await client.connect()
    await asyncio.sleep(3)

    # Test Report Command - should send back sensor values to notifier.py callbacks
    await client.send_report_command()
    client.set_idle_mode(True)


# async def test_sensor_swap(client: BleSmartLeaf):
#     global sensor_type
#     await client.connect()
#     await asyncio.sleep(3)
#
#     # Test Report Command - should send back sensor values to notifier.py callbacks
#     await client.send_report_command()
#     await asyncio.sleep(10)
#
#     #tomatoValues = SmartLeaf.query.filter(SmartLeaf.id==1).all() #filter nach pflanzenID dann nach sensor
#     #chili = SmartLeaf.query.filter(SmartLeaf.id==2).all()
#     #aloevera = SmartLeaf.query.filter(SmartLeaf.id==3).all()
#
#     vital_arr = []
#     sensor_type_of_interest = sensor_type  # specify the sensor type you're interested in
#
#     leafs = SmartLeaf.query.all()
#     for leaf in leafs:
#         vital_dict = {"id": leaf.id, "name": leaf.plant.name, "values": []}
#
#         # Get the most recent value for the specified sensor type
#         sensor_value = (
#             SensorData.query
#             .filter(SensorData.smart_leaf_id == leaf.id, SensorData.sensor_type_id == sensor_type_of_interest)
#             .order_by(SensorData.measured_on.desc())
#             .first()
#         )
#         if sensor_value is not None:
#             vital_dict["values"].append({
#                 "sensor_type": sensor_type_of_interest,
#                 "value": sensor_value.value,
#                 "measured_on": sensor_value.measured_on.isoformat(),
#             })
#
#         vital_arr.append(vital_dict)
#
#     for plant_data in vital_arr:
#         plant_id = plant_data['id']
#         plant_name = plant_data['name']
#         sensor_values = plant_data['values']
#
#     print(f"Data for {plant_name} (ID: {plant_id}):")
#
#     for value in sensor_values:
#         sensor_type = value['sensor_type']
#         sensor_value = value['value']
#         timestamp = value['measured_on']
#
#         print(f"  Sensor type: {sensor_type}")
#         print(f"  Value: {sensor_value}")
#         print(f"  Measured on: {timestamp}")
#         print("\n")
#
#         # For the first plant in the list
#     first_plant_data = vital_arr[0]
#     first_plant_values = first_plant_data['values']
#
#     # For the second plant in the list
#     second_plant_data = vital_arr[1]
#     second_plant_values = second_plant_data['values']
#
#     # For the second plant in the list
#     third_plant_data = vital_arr[2]
#     third_plant_values = third_plant_data['values']
#
#     #calculate scale for leds for watersensor
#     for plant_data in vital_arr:
#         latest_value = plant_data['values'][-1]['water_value']  # get the latest water value
#         water_min = ...  # retrieve this from the database or plant_data dictionary
#         water_max = ...  # retrieve this from the database or plant_data dictionary
#         num_leds = calculate_leds(latest_value, water_min, water_max)
#         print(f"Number of LEDs to light up for {plant_data['name']}: {num_leds}")
#
#     led_indexes = [i for i in num_leds]
#     for i in range(num_leds):
#         await client.send_set_neo_command([i], 0, 0, 255)
#         await asyncio.sleep(0.3)
#
#     sensor_type = (sensor_type+1)%3
#
#
#     #order: water-light-temp
# def calculate_leds(sensor_value, min_value, max_value):
#     # Check if the sensor_value is within the acceptable range
#     if sensor_value < min_value:
#         return 0
#     elif sensor_value > max_value:
#         return 8
#
#     # Calculate the percentage of the range that sensor_value represents
#     range_percentage = (sensor_value - min_value) / (max_value - min_value)
#
#     # Map this percentage to the number of LEDs (round to nearest whole number)
#     num_leds = round(range_percentage * 8)
#
#     return num_leds


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
