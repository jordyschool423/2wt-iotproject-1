# CTRL + SHIFT + P for commando palet
# Selecteer CircuitPython Serial Monitor -> Pico
# CTRL + C to start terminal

# CTRL-D to start program
# CTRL-C to stop program

# Library imports
import time
import analogio
import board
import digitalio
import adafruit_hcsr04

# Mediaan Library
def median(data):
    """Return the median (middle value) of numeric data.

    When the number of data points is odd, return the middle data point.
    When the number of data points is even, the median is interpolated by
    taking the average of the two middle values:

    >>> median([1, 3, 5])
    3
    >>> median([1, 3, 5, 7])
    4.0

    """
    data = sorted(data)
    n = len(data)
    if n % 2 == 1:
        return data[n // 2]
    else:
        i = n // 2
        return (data[i - 1] + data[i]) / 2



#           -------------------------------
#               Water Level Sensor Code
#           -------------------------------

# Use GPIO22 as a switch for the sensor
# Set GPIO22 as output
# Turn the power off
current = digitalio.DigitalInOut(board.GP22)
current.direction = digitalio.Direction.OUTPUT
current.value = False  

# Connect the sensor's analog input to A0
# (outside the function, otherwise it will try to open it multiple times)
waterlevel_sensor = analogio.AnalogIn(board.A0)


# Function to read the water level
def read_water_level():
    """
    Reads the water level from the sensor over 100 measurements
    returns an average value
    """
    current.value = True  # Turn the power on
    time.sleep(.05)  # Wait briefly for a stable reading
    waterlevelList = []
    for _ in range(100):  # Read 100 times (noise reduction)
        waterlevelList.append(waterlevel_sensor.value)
        time.sleep(0.002)  
    current.value = False  # Turn the power off
    return median(waterlevelList) #returns the median value (less sensitive to outliers)

def water_level_to_voltage(water_level):
    """
    Converts the water level reading to voltage.
    The water level is a 16-bit value (0-65535) from the sensor.
    """
    return (water_level / 65535) * 3.3  # Convert to voltage

def voltage_to_volume(voltage):
    """
    Turns voltage into volume in mL using a linear interpolation between calibration points.
    The calibration points are based on the following data:
    | Voltage (V) | Volume (mL) |
    |-------------|--------------|  
        0.03            0.0
        0.37            25.0
        0.88            50.0
        1.18            75.0
        1.22            100.0
        1.27            125.0
    """
    points = [
        (0.03, 0.0),
        (0.37, 25.0),
        (0.88, 50.0),
        (1.18, 75.0),
        (1.22, 100.0),
        (1.27, 125.0)
    ]

    if voltage <= points[0][0]:
        return 0.0
    if voltage >= points[-1][0]:
        return points[-1][1]

    for i in range(len(points) - 1):
        v0, ml0 = points[i]
        v1, ml1 = points[i+1]
        if v0 <= voltage <= v1:
            # Linear interpolation
            ratio = (voltage - v0) / (v1 - v0)
            return round(ml0 + ratio * (ml1 - ml0))
    return 0.0



#           -------------------------------
#               Ultrasonic Sensor Code
#           -------------------------------
#Before using the ultrasonic sensor, make sure to install the adafruit_hcsr04 library 
#in your CircuitPython environment.


# Set up the trigger and echo pins
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP19, echo_pin=board.GP18)

def read_ultrasonic_distance():
    """
    Reads the distance from the ultrasonic sensor.
    Returns the distance in centimeters.
    """
    distanceList = []
    for _ in range(5):  # Read 5 times for stability
        try:
            distanceList.append(sonar.distance)
        except RuntimeError:
            pass # skip failed reading

        time.sleep(0.1)  # Short delay between readings

        if not distanceList:  # If all readings failed, return a default value
            return None
        
    return median(distanceList)  # Returns median distance in centimeters

def distance_to_volume(distance):
    """
    Converts the ultrasonic distance in cm to a volume in mL using
    linear interpolation between the calibration points.
    Calibration points (distance in cm, volume in mL):
    | Distance (cm) | Volume (mL) |
    |---------------|-------------|
        6.48            0.0
        5.53            25.0
        4.56            50.0
        3.26            75.0
        2.94            100.0
        2.62            125.0
    Note: distance is inversely related to volume (closer = more water),
    so the points are ordered from high distance (empty) to low distance (full).
    """
    points = [
        (6.48, 0.0),
        (5.53, 25.0),
        (4.56, 50.0),
        (3.26, 75.0),
        (2.94, 100.0),
        (2.62, 125.0)
    ]

    # Below the lowest calibration distance -> beaker is full
    if distance <= points[-1][0]:
        return points[-1][1]
    # Above the highest calibration distance -> beaker is empty
    if distance >= points[0][0]:
        return 0.0

    for i in range(len(points) - 1):
        d0, ml0 = points[i]
        d1, ml1 = points[i + 1]
        if d0 >= distance >= d1:
            # Linear interpolation
            ratio = (d0 - distance) / (d0 - d1)
            return round(ml0 + ratio * (ml1 - ml0))

    return 0.0

#           -------------------------------
#                      Main loop
#           -------------------------------

def combined_volume(volume_wls, volume_us):
    """
    Combines the two volume estimates.
    Ultrasonic is more accurate at higher volumes, WLS at lower volumes,
    so use a weighted average.
    """
    w_us = 0.75  # weight for the ultrasonic estimate
    w_wls = 0.25  # weight for the WLS estimate
    return round(w_us * volume_us + w_wls * volume_wls)


try:
    while True:
        # loop start
        input("Press Enter to read water level... (CTRL + C to stop)")

        # Water Level Sensor Reading
        print("---Water Level Sensor Reading---")
        water_level = read_water_level() #read water level from sensor
        voltage = water_level_to_voltage(water_level)
        print("Voltage from WLS:", f"{voltage:.2f}V")
        WLS_volume = voltage_to_volume(voltage)
        print("Volume from WLS:", f"{WLS_volume:.0f}mL")

        # Ultrasonic Sensor Reading
        print("\n---Ultrasonic Sensor Reading---")
        distance = read_ultrasonic_distance()
        print("Distance from Ultrasonic Sensor:", f"{distance:.2f}cm")
        US_volume = distance_to_volume(distance)
        print("Volume from Ultrasonic Sensor:", f"{US_volume:.0f}mL")

        # Combined Volume Estimate
        print("\n---Combined Volume Estimate---")
        combined = combined_volume(WLS_volume, US_volume)
        print("Combined Volume Estimate:", f"{combined:.0f}mL")

# CTRL + C to stop the program
except KeyboardInterrupt:
    print("\nProgram stopped by user.")


