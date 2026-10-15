import time
import analogio
import board
import digitalio


# Use GPIO22 as a switch for the sensor
# Set GPIO22 as output
# Turn the power off
current = digitalio.DigitalInOut(board.GP22)
current.direction = digitalio.Direction.OUTPUT
current.value = True  

# Connect the sensor's analog input to A0
# (outside the function, otherwise it will try to open it multiple times)
waterlevel_sensor = analogio.AnalogIn(board.A0)


# Function to read the water level
def read_water_level():
    """
    Reads the water level from the sensor over 10 measurements
    returns an average value
    """
    current.value = False  # Turn the power on
    time.sleep(5)  # Wait briefly for a stable reading
    waterlevelList = []
    for _ in range(100):  # Read 100 times (noise reduction)
        waterlevelList.append(waterlevel_sensor.value)
        time.sleep(0.01)  
    current.value = True  # Turn the power off
    return waterlevelList[50] #returns the median value (less sensitive to outliers)
