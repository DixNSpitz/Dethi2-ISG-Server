# import struct
#
# from flask import current_app
# from isg_api.models import SmartLeaf, SensorData, SensorType
#
# notify_uuid_dict = {
#     'luminosity': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2B01),
#     'soil_humidity': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A6F),
#     'batt': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2BF0),
#     'touch': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A6D),
# }
#
#
# class Notifier:
#     def __init__(self, report_lum_callback=None,  report_hum_callback=None, touch_callback=None):
#         self._report_lum_callback = report_lum_callback
#         self._report_hum_callback = report_hum_callback
#         self._touch_callback = touch_callback
#         self._ignore_custom_callbacks = False
#
#     def set_report_lum_callback(self, callback):
#         self._report_lum_callback = callback
#
#     def set_report_hum_callback(self, callback):
#         self._report_hum_callback = callback
#
#     def set_touch_callback(self, callback):
#         self._touch_callback = callback
#
#     def set_ignore_custom_callbacks(self, ignore_custom_callbacks):
#         self._ignore_custom_callbacks = ignore_custom_callbacks
#
#     def ble_callback(self, client, address, characteristic, data, print_details=False):
#         if print_details:
#             print('mac:', address, ', characteristic:', characteristic, ', data:', data)
#
#         if not self._ignore_custom_callbacks:
#             if characteristic.uuid == notify_uuid_dict['luminosity'] and self._report_lum_callback:
#                 value = struct.unpack('d', data)[0]
#                 self._report_lum_callback(client, value)
#                 return
#             elif characteristic.uuid == notify_uuid_dict['soil_humidity'] and self._report_hum_callback:
#                 value = struct.unpack('d', data)[0]
#                 self._report_hum_callback(client, value)
#                 return
#             elif characteristic.uuid == notify_uuid_dict['touch'] and self._touch_callback:
#                 value = struct.unpack('<i', data)[0]  # 0 = short, 1 = long
#                 self._touch_callback(client, value)
#                 return
#
#         with current_app.app_context():
#             leaf = SmartLeaf.query.filter(SmartLeaf.mac_address == address).first()
#             if leaf:
#                 datapoint = SensorData()
#                 datapoint.smart_leaf_id = leaf.id
#
#                 datatype = None
#                 value = None
#                 if characteristic.uuid == notify_uuid_dict['luminosity']:
#                     datatype = db.session.query(SensorType).filter(SensorType.id == 1).first() # Luminosity
#                     value = struct.unpack('d', data)[0]
#                     print('Luminosity value received:', value)
#                 elif characteristic.uuid == notify_uuid_dict['soil_humidity']:
#                     datatype = db.session.query(SensorType).filter(SensorType.id == 2).first() # Humidity
#                     value = struct.unpack('d', data)[0]
#                     print('Humidity value received:', value)
#                 elif characteristic.uuid == notify_uuid_dict['batt']:
#                     datatype = db.session.query(SensorType).filter(SensorType.id == 4).first() # Percentage
#                     value = struct.unpack('<i', data)[0]
#                     print('Battery value received:', value)
#                 elif characteristic.uuid == notify_uuid_dict['touch']:
#                     # TODO important for games => notify game state!
#                     value = struct.unpack('<i', data)[0] # 0 = short, 1 = long
#                     print('Touch value received:', value)
#                     return
#
#                 if datatype is not None and value is not None:
#                     datapoint.sensor_type_id = datatype.id
#                     datapoint.value = value
#
#                     db.session.add(datapoint)
#                     db.session.commit()
