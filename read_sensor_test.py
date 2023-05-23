import smbus
import time

# Initialize I2C (Inter-Integrated Circuit) bus
bus = smbus.SMBus(1)

# Sensor address is 0x44 (68 in decimal)
# First parameter = sensor's address
# Second parameter = command to the sensor to begin measuring
# Third parameter = instructs the sensor to take a high repeatability measurement
bus.write_i2c_block_data(0x44, 0x2C, [0x06])

time.sleep(0.5)

# Read the data from the sensor
# First parameter = sensor's address
# Second parameter = address to read from
# Third parameter = number of bytes to read
data = bus.read_i2c_block_data(0x44, 0x00, 6)

# Convert the raw data bytes to actual temperature and humidity values
temp = data[0] * 256 + data[1]
cTemp = -45 + (175 * temp / 65535.0)
fTemp = -49 + (315 * temp / 65535.0)
humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

# Output temperature and humidity values
print ("Temperature in Celsius is : %.2f C" %cTemp)
print ("Temperature in Fahrenheit is : %.2f F" %fTemp)
print ("Relative Humidity is : %.2f %%RH" %humidity)