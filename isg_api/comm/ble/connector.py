import asyncio

from bleak import BleakClient
from isg_api.globals import db
from isg_api.models import SmartLeaf

temperatureUUID = "45366e80-cf3a-11e1-9ab4-0002a5d5c51b"
ecgUUID = "46366e80-cf3a-11e1-9ab4-0002a5d5c51b"

notify_uuid = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(0xFFE1) # TODO!!!!! uuid for client touch input!


def callback(address, characteristic, data):
    print('mac:', address, 'char:', characteristic, 'data:', data)


async def connect_to_device(address):
    print("starting", address, "loop")
    async with BleakClient(address, timeout=5.0) as client:

        print("connect to", address)
        try:
            await client.start_notify(notify_uuid, lambda x, y: callback(address, x, y))
            await asyncio.sleep(10.0) # TODO longer than 10 seconds => actually infinite
            await client.stop_notify(notify_uuid)
        except Exception as e:
            print(e)

    print("disconnect from", address)


def __connect_to_leafs__(addresses):
    return asyncio.gather(*(connect_to_device(address) for address in addresses))


def connect_to_leafs():
    # First get all of the BLE-device adresses from the DB
    macs = db.session.query(SmartLeaf.mac_address).all()
    macs = [mac[0] for mac, in macs]

    # Then try to connect to every BLE-device
    asyncio.run(__connect_to_leafs__(macs))