import asyncio
import struct
import time

from bleak import BleakClient
from isg_api.globals import scheduler, db
from isg_api.models import SmartLeaf, SensorData, SensorType

notify_uuid_dict = {
    'luminosity': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2B01),
    'soil_humidity': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A6F),
    'batt': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2BF0),
    'touch': '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A6D),
}

def _calculate_leds(sensor_value, min_value, max_value):
    # Check if the sensor_value is within the acceptable range
    if sensor_value < min_value:
        return 0
    elif sensor_value > max_value:
        return 8

    # Calculate the percentage of the range that sensor_value represents
    range_percentage = (sensor_value - min_value) / (max_value - min_value)

    # Map this percentage to the number of LEDs (round to nearest whole number)
    num_leds = round(range_percentage * 8)

    return num_leds


class BleSmartLeaf:
    _notify_uuid_report = '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A4D)
    _notify_uuid_set_neo = '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2BE2)

    def __init__(self, address, print_exception_details=False):
        self.address = address
        #self._reset_client()
        self.client = BleakClient(address)
        self._print_exception_details = print_exception_details
        self._idle_time_started = None
        self._idle_mode = True
        self._idle_mode_lum = True

    def set_idle_mode(self, on):
        self._idle_mode = on
        if not on: self._idle_time_started = None

    def _reset_client(self):
        print('reset client...')
        # self.client = BleakClient(self.address)

    async def _hook_callbacks(self):
        print('Hooking callbacks')
        for notify_uuid in notify_uuid_dict.values():
            await self.client.start_notify(notify_uuid, self.ble_callback)
        self.client.set_disconnected_callback(self._disconnect_callback)

    async def connect(self, retries=2):
        if self.client.is_connected:
            return True

        retry_ct = 0
        while retry_ct < retries and not self.client.is_connected:
            self._log('Trying to connect', '({0})'.format(retry_ct + 1))
            try:
                await self.client.connect()
            except Exception as e:
                self._log('Exception was thrown while connecting')
                if self._print_exception_details: print(e)
                retry_ct += 1

        if self.client.is_connected:
            # if retry_ct == retries:
            #    await self.disconnect()
            #    return False

            # Hook all notifiers
            try:
                await self._hook_callbacks()
                self.client.set_disconnected_callback(self._disconnect_callback)
            except Exception as e:
                self._log('Exception was thrown while trying to hook notifiers')
                if self._print_exception_details: print(e)
                await self.disconnect()
                self._reset_client()
                return False

            self._log('Connected')
            return True
        else:
            self._log('Could not connect')
            self._reset_client()
            return False

    async def disconnect(self):
        if self.client.is_connected:
            try:
                await self.client.disconnect()
            except Exception as e:
                self._log('Exception was thrown while trying to disconnect')
                if self._print_exception_details: print(e)

    async def send_report_command(self, report_lum=True, report_hum=True, connect_if_not_connected=True):
        if connect_if_not_connected and self.client.is_connected:
            await self.connect()

        if self.client.is_connected:
            # Send initial report command
            self._log('Trying to write report command')
            if report_lum and report_hum: cmd_flag = 0
            elif report_lum: cmd_flag = 1
            elif report_hum: cmd_flag = 2
            else: cmd_flag = None
            if cmd_flag is None:
                self._log('Please set a report Flag')
                return

            await self.client.write_gatt_char(self._notify_uuid_report, struct.pack('H', cmd_flag))
            self._log('Report command write finished')

    async def send_set_neo_command(self, led_indexes, r, g, b, clear_other_leds_flag=True, connect_if_not_connected=True):
        if connect_if_not_connected and self.client.is_connected:
            await self.connect()

        if self.client.is_connected:
            # Send initial report command
            self._log('Trying to write set-neo command')
            ctrl_str = '1' if clear_other_leds_flag else '2'
            for i in range(8):
                ctrl_str += '1' if i in led_indexes else '0'

            await self.client.write_gatt_char(self._notify_uuid_set_neo, struct.pack('IHHH', int(ctrl_str), r, g, b))
            self._log('Set-neo command write finished')

    async def send_set_neo_clear_all(self, connect_if_not_connected=True):
        if connect_if_not_connected and self.client.is_connected:
            await self.connect()

        if self.client.is_connected:
            # Send initial report command
            self._log('Trying to write set-neo clear command')
            await self.client.write_gatt_char(self._notify_uuid_set_neo, struct.pack('IHHH', int('100000000'), 0, 0, 0))
            self._log('Set-neo clear command write finished')

    async def ble_callback(self, characteristic, data):
        print('mac:', self.address, ', characteristic:', characteristic, ', data:', data)

        with scheduler.app.app_context():
            print('In App Context!')
            leaf = SmartLeaf.query.filter(SmartLeaf.mac_address == self.address).first()
            if leaf:
                print('Got leaf!')
                datapoint = SensorData()
                datapoint.smart_leaf_id = leaf.id

                datatype = None
                value = None
                touch = False
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
                    touch = True
                    if self._idle_mode:
                        self._idle_time_started = time.time()
                        self._idle_mode_lum = not self._idle_mode_lum

                if not touch and datatype is not None and value is not None:
                    datapoint.sensor_type_id = datatype.id
                    datapoint.value = value

                    db.session.add(datapoint)
                    db.session.commit()

                # continue with asking
                if self._idle_mode and self._idle_time_started is not None:
                    print('in idle mode func...')
                    if time.time() - self._idle_time_started > 60:
                        print('Idle mode terminated...')
                        self._idle_time_started = None
                        return

                    elif datatype is not None and value is not None:
                        min = leaf.plant.light_min if datatype.id == 1 else leaf.plant.water_min
                        max = leaf.plant.light_max if datatype.id == 1 else leaf.plant.water_max
                        print('dt.id:', datatype.id, 'min:', min, 'max:', max)
                        how_many_leds = _calculate_leds(value, min, max)
                        print('want to show', how_many_leds, 'leds')
                        led_idxs = []
                        for i in range(how_many_leds): led_idxs.append(i)
                        r = 255 if datatype.id == 1 else 0
                        g = 255 if datatype.id == 1 else 0
                        b = 255
                        print('sending off neo command')
                        await self.send_set_neo_command(led_idxs, r, g, b)
                        await asyncio.sleep(1)

                    print('sending off next report command - keep asking for sensor values...')
                    await self.send_report_command(self._idle_mode_lum, not self._idle_mode_lum)

    def _log(self, *values: object):
        a = list(values)
        a.insert(0, '[Smart-Leaf: {0}]'.format(self.address))
        values = tuple(a)
        print(*values)

    def _disconnect_callback(self, client):
        # for notify_uuid in notify_uuid_dict.values():
        # await self.client.stop_notify(notify_uuid)
        self._log('Disconnected')
        self._reset_client()
