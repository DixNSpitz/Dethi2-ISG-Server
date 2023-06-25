import struct

from bleak import BleakClient
from isg_api.comm.ble.notifier import ble_callback, notify_uuid_dict


class BleSmartLeaf:
    _notify_uuid_report = '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A4D)
    _notify_uuid_set_neo = '0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2BE2)

    def __init__(self, address, print_exception_details=False):
        self.address = address
        self._reset_client()
        self._print_exception_details = print_exception_details

    def _reset_client(self):
        self.client = BleakClient(self.address)

    async def connect(self, retries=2):
        if self.client.is_connected: return True

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
            if retry_ct == retries:
                await self.disconnect()
                return False

            # Hook all notifiers
            try:
                for notify_uuid in notify_uuid_dict.values():
                    await self.client.start_notify(notify_uuid, lambda x, y: ble_callback(self.address, x, y, True))
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

    async def send_report_command(self, connect_if_not_connected=True):
        if connect_if_not_connected and self.client.is_connected:
            await self.connect()

        if self.client.is_connected:
            # Send initial report command
            self._log('Trying to write report command')
            await self.client.write_gatt_char(self._notify_uuid_report, struct.pack('<i', 12345))
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
