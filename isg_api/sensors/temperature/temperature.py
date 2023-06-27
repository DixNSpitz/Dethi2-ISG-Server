import smbus
import time

class SenseTemperature:
    def __init__(self, bus_idx, addr, cmd, mode):
        self.bus = smbus.SMBus(bus_idx)
        self.addr = addr
        # Send measurement command to the SHT30
        self.bus.write_i2c_block_data(self.addr, cmd, mode)
        time.sleep(0.5)

    def read(self):
        # Read 6 bytes from the sensor
        data = self.bus.read_i2c_block_data(self.addr, 0x00, 6)
        # Convert the raw data bytes to actual temperature and humidity values
        temp = data[0] * 256 + data[1]
        cTemp = -45 + (175 * temp / 65535.0)
        fTemp = -49 + (315 * temp / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
        return cTemp, fTemp, humidity