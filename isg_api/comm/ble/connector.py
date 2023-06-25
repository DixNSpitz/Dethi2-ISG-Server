import asyncio
import struct

from bleak import BleakClient
from isg_api.comm.ble.notifier import ble_callback, notify_uuid_dict

notify_uuid_report ='0000{0:x}-0000-1000-8000-00805f9b34fb'.format(0x2A4D)


async def connect_to_device(address, print_service_details=False):
    print("connecting to Smart-Leaf with address:", address)
    try:
        async with BleakClient(address, timeout=7.0) as client:
            print("connect to", address)

            if print_service_details:
                print('describing services and characteristics')
                for s in client.services:
                    print('service.uuid:', s.uuid, 'service.description:', s.description)
                    for c in s.characteristics:
                        print('char.uuid:', c.uuid, 'char.description:', c.description)

            try:
                for notify_uuid in notify_uuid_dict.values():
                    await client.start_notify(notify_uuid, lambda x, y: ble_callback(address, x, y, True))

                # wait 10 seconds for response
                print('write to report char')
                await client.write_gatt_char(notify_uuid_report, struct.pack('<i', 12345)) # TODO create command table => 0 send back sensor data, 125500000011000000 => e.g. display two red LEDs
                print('write finished')
                await asyncio.sleep(40.0)

                for notify_uuid in notify_uuid_dict.values():
                    await client.stop_notify(notify_uuid)
            except Exception as e:
                print(e)

        print("disconnect from", address)
    except Exception as e:
        print('Could not connect to:', address)
        print(e)


async def connect_to_devices(addresses, print_service_details=False):
    return await asyncio.gather(*(connect_to_device(address, print_service_details) for address in addresses))
