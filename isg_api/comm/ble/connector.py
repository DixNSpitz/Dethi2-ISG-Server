import asyncio

from bleak import BleakClient

temperatureUUID = "45366e80-cf3a-11e1-9ab4-0002a5d5c51b"
ecgUUID = "46366e80-cf3a-11e1-9ab4-0002a5d5c51b"

notify_uuid = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(0xFFE1) # TODO!!!!! uuid for client touch input!


def callback(address, characteristic, data):
    print('mac:', address, 'char:', characteristic, 'data:', data)


async def connect_to_device(address):
    print("starting", address, "loop")
    try:
        async with BleakClient(address, timeout=5.0) as client:

            print("connect to", address)
            try:
                await client.start_notify(notify_uuid, lambda x, y: callback(address, x, y))
                await asyncio.sleep(10.0) # TODO longer than 10 seconds => actually infinite
                await client.stop_notify(notify_uuid)
            except Exception as e:
                print(e)

        print("disconnect from", address)
    except Exception as e:
        print('Could not connect to:', address)
        print(e)


async def connect_to_devices(addresses):
    return await asyncio.gather(*(connect_to_device(address) for address in addresses))
