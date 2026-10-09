import time
import board
import busio

from adafruit_ads1x15 import ads1x15
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# activeert het I2C-protocol op GPIO 2 (SDA) en GPIO 3 (SCL).
i2c = busio.I2C(board.SCL, board.SDA)
# initialiseert de communicatie met de chip via het standaard I2C-adres
ads = ADS.ADS1115(i2c)

chan = AnalogIn(ads, ads1x15.Pin.A0)

print("starten met Voltage-meting (5sec)")

try:
    while True:
        print(f"Spanning: {chan.voltage:.2f}V")
        time.sleep(5)
except KeyboardInterrupt:
    print("Meting gestopt door user")
