# from isg_api.comm.ble.smart_leaf import BleSmartLeaf
# from isg_api.globals import scheduler
# from isg_api.models import SmartLeaf, Plant
#
#
# async def callback_touch(client: BleSmartLeaf, value):
#     if value is None:
#         return
#
#     if value == 1 or value == 2:
#         await client.send_report_command(True, False) # only luminosity
#
#
# async def callback_lum(client: BleSmartLeaf, value):
#     if value is None:
#         return
#
#     with scheduler.app.app_context():
#         plant = SmartLeaf.query.filter(SmartLeaf.mac_address == client.address).first().plant
#         if plant is not None:
#             min_lum = plant.light_min
#             max_lum = plant.light_max
#             led_count = _calculate_leds(value, min_lum, max_lum)
#             led_idxs = []
#             for i in range(led_count):
#                 led_idxs.append(i)
#
#             await client.send_set_neo_command(led_idxs, 0, 0, 255)
#
#
# def callback_hum(client: BleSmartLeaf, value):
#     return
#
#
# def _calculate_leds(sensor_value, min_value, max_value):
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