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
import adafruit_rgbled

# Wifi imports
import wifi
import os
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Median Library
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
#                Wifi connection Code
#           -------------------------------

connection_interval = 10
last_try = -connection_interval    #initialisatie is -interval zodat hij connectie probeert te maken vanaf het moment dat hij gepowered word

def wifi_connection():
    global last_try               #global = variabele die buiten deze functie zich bevind, anders maakt hij er een nieuwe van
    if wifi.radio.connected:
        return

    if time.monotonic() -last_try < connection_interval:   #time.monotonic is een klok die enkel opteld -> goed om tijdsverschillen in een programma te meten
        return
    
    last_try = time.monotonic()       # moet voor de try anders voert die enkel uit bij een succes
    try:
        print("connecting to wifi")
        wifi.radio.connect(os.getenv("WIFI_SSID"),os.getenv("WIFI_PASSWORD"),timeout= 10)   #timeout op 10 gezet, met 3 begonnen maar was te kort.
        print(f"connected to wifi as {wifi.radio.ipv4_address}")
    except(ConnectionError, TimeoutError) as e:
        print("error",e)


#           -------------------------------
#                MQTT connection Code
#           -------------------------------


pool = socketpool.SocketPool(wifi.radio)
mqtt_client = MQTT.MQTT(
                                broker="mqtt3.thingspeak.com",
                                username= os.getenv("THINGSPEAK_UNAME"),
                                password=os.getenv("THINGSPEAK_PASSWD"),
                                client_id=os.getenv("CLIENT_ID"),
                                is_ssl= True,
                                socket_pool=pool,
                                ssl_context= ssl.create_default_context()   #ssl want anders word alles blijkbaar in plain text doorgestuurd
                                )

# MQTT connect function
def connect_mqtt():
    print("MQTT connection started")
    if not wifi.radio.connected:
        print("Wifi not connected")
        return
    if mqtt_client._is_connected:
        print("MQTT already connected")
        return
    try:
        print("connecting to MQTT broker")
        mqtt_client.connect()
        print("MQTT connection succesfull")
    except Exception as e:
        print(f"MQTT error: {e}")


# MQTT publish function
CHAN_ID = os.getenv("CHAN_ID")
PUBLISH_TOPIC = f"channels/{CHAN_ID}/publish"

publish_interval = 20
last_publish = time.monotonic()

def publish_MQTT(WLS_volume, US_volume, estimated_volume, tank_distance):
    global last_publish
    if time.monotonic() - last_publish > publish_interval:
        last_publish = time.monotonic()
        payload = f"field1={WLS_volume:.0f}&field2={US_volume:.0f}&field3={estimated_volume:.0f}&field4={tank_distance:.0f}"
        try:
            mqtt_client.publish(PUBLISH_TOPIC, payload)
            print("published:", payload)
        except Exception as e:
            print("MQTT publish error:", e)
            try:
                mqtt_client.disconnect()
            except Exception:
                pass


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
#              Ultrasonic Sensor Code CUP
#           -------------------------------
#Before using the ultrasonic sensor, make sure to install the adafruit_hcsr04 library 
#in your CircuitPython environment.


# Set up the trigger and echo pins
sonar_cup = adafruit_hcsr04.HCSR04(trigger_pin=board.GP19, echo_pin=board.GP18)

def read_ultrasonic_distance_cup():
    """
    Reads the distance from the ultrasonic sensor in the cup.
    Returns the distance in centimeters.
    """
    distanceList = []
    for _ in range(5):  # Read 5 times for stability
        try:
            distanceList.append(sonar_cup.distance)
        except RuntimeError:
            pass # skip failed reading

        time.sleep(0.1)  # Short delay between readings

        if not distanceList:  # If all readings failed, return a default value
            return None
        
    return median(distanceList)  # Returns median distance in centimeters

def distance_to_volume_cup(distance):
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
#              Ultrasonic Sensor Code TANK
#           -------------------------------
sonar_tank = adafruit_hcsr04.HCSR04(trigger_pin=board.GP15, echo_pin=board.GP14)

max_high_distance = 15  # cm, distance when the tank is empty

def read_ultrasonic_height_tank():
    """
    Reads the height of the water in the tank from the ultrasonic sensor.
    Returns the height in centimeters.
    """
    distanceList = []
    i = 0
    for _ in range(5):  # Read 5 times for stability
        i += 1
        try:
            distanceList.append(sonar_tank.distance)
        except RuntimeError:
            print(f"Reading {i}: Ultrasonic sensor tank reading failed. Skipping this reading.")
            pass # skip failed reading

        time.sleep(0.1)  # Short delay between readings

        if not distanceList:  # If all readings failed, return a default value
            return None
        
    # Returns median height in centimeters water remaining (15 cm is the max height when empty)
    result = max_high_distance - median(distanceList)
    if result < 0:
        return 0
    else:
        return result


#           -------------------------------
#                 LED Indicator Code
#           -------------------------------


# Define LED thresholds for the tank's water level
LED_yellow_light_treshold = 10  # cm
LED_red_light_treshold = 5      # cm

# Set up LED pins

led = adafruit_rgbled.RGBLED(board.GP4, board.GP2, board.GP3)

red_color = 255
green_color = 0
blue_color = 0
    

def led_tank_water_level(height):
    """
    Controls the LED indicators based on the water height in the tank.
    - Green LED: Water level is above 10cm height. (safe level)
    - Yellow LED: Water level is between 5cm and 10cm height. (warning level)
    - Red LED: Water level is below 5cm height. (critical level)
    """
    print(f"LED Control: Water height = {height:.0f} cm")
    if height > LED_yellow_light_treshold:
        led.color = (0, 0, 255)  # Green
    elif height > LED_red_light_treshold:
        led.color = (255, 0, 150)  # Yellow
    elif height >= 0:
        led.color = (255, 0, 0)  # Red
    else:
        led.color = (255, 255, 255)  # White (error state)
        print("Error in LED control)")


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
    # Default LED
    led.color = (255, 255, 255)  # White (default state) 
    while True:
        # Loop start

        # Wifi and MQTT connection
        wifi_connection()
        if wifi.radio.connected and not mqtt_client.is_connected():
            connect_mqtt()

        
        input("Press Enter to read water level... (CTRL + C to stop)")
        # time.sleep(1)  # Wait for 1 second before reading sensors

        # Water Level Sensor Reading
        print("---Water Level Sensor Reading---")
        water_level = read_water_level() #read water level from sensor
        voltage = water_level_to_voltage(water_level)
        print("Voltage from WLS:", f"{voltage:.2f}V")
        WLS_volume = voltage_to_volume(voltage)
        print("Volume from WLS:", f"{WLS_volume:.0f}mL")

        # Ultrasonic Sensor Reading cup
        print("\n---Ultrasonic Sensor Reading---")
        distance = read_ultrasonic_distance_cup()
        print("Distance from Ultrasonic Sensor:", f"{distance:.2f}cm")
        US_volume = distance_to_volume_cup(distance)
        print("Volume from Ultrasonic Sensor:", f"{US_volume:.0f}mL")

        # Combined Volume Estimate
        print("\n---Combined Volume Estimate---")
        combined = combined_volume(WLS_volume, US_volume)
        print("Combined Volume Estimate:", f"{combined:.0f}mL")

        # Tank Ultrasonic Sensor Reading
        print("\n---Tank Ultrasonic Sensor Reading---")
        tank_height = read_ultrasonic_height_tank()
        print("Height water in tank:", f"{tank_height:.0f}cm")

        # Publish to MQTT
        if wifi.radio.connected and mqtt_client.is_connected():
            publish_MQTT(WLS_volume, US_volume, combined, tank_height)

        # LED Indicator Control
        print("\n---LED Indicator Control---")
        led_tank_water_level(tank_height)


# CTRL + C to stop the program
except KeyboardInterrupt:
    print("\nProgram stopped by user.")
