import struct

from isg_api.globals import scheduler, db
from isg_api.models import SmartLeaf, SensorData, SensorType

notify_uuid_dict = {
    'luminosity': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2B01),
    'soil_humidity': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A6F),
    'batt': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2BF0),
    'touch': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A6D),
}


def ble_callback(address, characteristic, data, print_details=False):
    if print_details:
        print('mac:', address, ', characteristic:', characteristic, ', data:', data)

    with scheduler.app.app_context():
        leaf = SmartLeaf.query.filter(SmartLeaf.mac_address == address).first()
        if leaf:
            datapoint = SensorData()
            datapoint.smart_leaf_id = leaf.id

            datatype = None
            value = None
            if characteristic.uuid == notify_uuid_dict['luminosity']:
                datatype = db.session.query(SensorType).filter(SensorType.id == 1).first() # Luminosity
                value = struct.unpack('d', data)[0]
                print('Luminosity value received:', value)
            elif characteristic.uuid == notify_uuid_dict['soil_humidity']:
                datatype = db.session.query(SensorType).filter(SensorType.id == 2).first() # Humidity
                value = struct.unpack('d', data)[0]
                print('Humidity value received:', value)
            elif characteristic.uuid == notify_uuid_dict['batt']:
                datatype = db.session.query(SensorType).filter(SensorType.id == 4).first() # Percentage
                value = struct.unpack('<i', data)[0]
                print('Battery value received:', value)
            elif characteristic.uuid == notify_uuid_dict['touch']:
                # TODO important for games => notify game state!
                value = struct.unpack('<i', data)[0] # 0 = short, 1 = long
                print('Touch value received:', value)
                return

            if datatype is not None and value is not None:
                datapoint.sensor_type_id = datatype.id
                datapoint.value = value

                db.session.add(datapoint)
                db.session.commit()
