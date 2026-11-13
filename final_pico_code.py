# Library imports
import time
import board
import digitalio
import adafruit_hcsr04
import adafruit_rgbled
import busio
from i2ctarget import I2CTarget
import traceback

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
    # print("MQTT connection started")
    if mqtt_client.is_connected:
        # print("MQTT already connected")
        return
    try:
        print("connecting to MQTT broker")
        mqtt_client.connect()
        print("MQTT connection succesful")
    except Exception as e:
        print(f"MQTT error: {e}")


# MQTT publish function
CHAN_ID = os.getenv("CHAN_ID")
PUBLISH_TOPIC = f"channels/{CHAN_ID}/publish"

publish_interval = 20
last_publish = time.monotonic()

def publish_MQTT(US_volume,tank_distance):
    global last_publish
    if time.monotonic() - last_publish > publish_interval:
        last_publish = time.monotonic()
        payload = f"field1={US_volume:.0f}&field2={tank_distance:.2f}"
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
#              Ultrasonic Sensor Code CUP
#           -------------------------------

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
            # print(distanceList)
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
        13.57           0.0
        13.23           25.0
        12.87           50.0
        12.42           75.0
        11.53           100.0
        11.19           125.0
    Note: distance is inversely related to volume (closer = more water),
    so the points are ordered from high distance (empty) to low distance (full).
    """
    points = [
        (13.57, 0),
        (13.23, 25),
        (12.87, 50),
        (12.42, 75),
        (11.53, 100),
        (11.19, 125)
    ]

    # Below the lowest calibration distance -> beaker is full
    if distance <= points[-1][0]:
        return points[-1][1]
    # Above the highest calibration distance -> beaker is empty
    if distance >= points[0][0]:
        return 0

    for i in range(len(points) - 1):
        d0, ml0 = points[i]
        d1, ml1 = points[i + 1]
        if d0 >= distance >= d1:
            # Linear interpolation
            ratio = (d0 - distance) / (d0 - d1)
            return round(ml0 + ratio * (ml1 - ml0))

    return 0

#           -------------------------------
#              Ultrasonic Sensor Code TANK
#           -------------------------------
sonar_tank = adafruit_hcsr04.HCSR04(trigger_pin=board.GP16, echo_pin=board.GP17)

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

LED_yellow_light_threshold = 10  # cm
LED_red_light_threshold = 7      # cm

# Set up LED pins

led = adafruit_rgbled.RGBLED(board.GP27, board.GP26, board.GP22)

def led_tank_water_level(height):
    """
    Controls the LED indicators based on the water height in the tank.
    - Green LED: Water level is above 10cm height. (safe level)
    - Yellow LED: Water level is between 5cm and 10cm height. (warning level)
    - Red LED: Water level is below 5cm height. (critical level)
    """
    # print(f"LED Control: Water height = {height:.0f} cm")
    if height > LED_yellow_light_threshold:
        led.color = (0, 255, 0)  # Green
    elif height > LED_red_light_threshold:
        led.color = (255, 150, 0)  # Yellow
    elif height >= 0:
        led.color = (255, 0, 0)  # Red
    else:
        led.color = (255, 255, 255)  # White (error state)
        # print("Error in LED control)")
    
#           -------------------------------
#                    pump control
#           -------------------------------

pump = digitalio.DigitalInOut(board.GP21)
pump.direction = digitalio.Direction.OUTPUT

# laagste punt van het glas(of vanaf waar hij moet beginnen met vullen) in cm
start_fill = 25
# punt vanaf waar hij moet stoppen met vullen in cm
stop_fill = 75
#geeft waarde terug of pomp moet aanslaan of niet
def set_pump(on_off):
    pump.value = on_off

def next_state(volume, filling):
    if not filling and volume < start_fill:
        return True
    if filling and volume > stop_fill:
        return False
    
    #behoud de stand van de pomp als de status niet moet veranderen
    return filling

#           -------------------------------
#                        I2C
#           -------------------------------

def send_i2c():      
    try: 
        if sonar_cup.distance<6:
            volume = 999
        else:
            volume = int(US_volume)
        request = target.request(timeout=2)
        if request:
            with request:
                if request.is_read:
                    print(volume.to_bytes(2,"big"))
                    request.write(volume.to_bytes(2, "big"))
    except Exception as e:
            print("I2C ERROR:", e)
#           -------------------------------
#                      Main loop
#           -------------------------------

filling = False
set_pump(filling)
PI_ADDR = 0x42

US_volume = 0
target = I2CTarget(board.GP11, board.GP10, (0x42,))

led.color = (255, 255, 255)  # White (default state) 

while True:
    try:
        # Wifi and MQTT connection
        if not filling:
            wifi_connection()
            if not mqtt_client.is_connected() and wifi.radio.connected:
                connect_mqtt()

        # Ultrasonic Sensor Reading cup
        distance = read_ultrasonic_distance_cup()
        if distance is None:
            print("cup sensor failed, pump off")
            set_pump(False)
            filling = False
            time.sleep(1)
            continue
        else:
            print("Distance from Ultrasonic Sensor:", f"{distance:.2f}cm")
        
        US_volume = distance_to_volume_cup(distance)

        # Tank Ultrasonic Sensor Reading
        tank_height = read_ultrasonic_height_tank()
        if tank_height is None:
            print("tank sensor failed, pump off")
            set_pump(False)
            filling = False
            time.sleep(1)
            continue
        
        # Publish to MQTT
        if wifi.radio.connected and mqtt_client.is_connected() and mqtt_ready:
            publish_MQTT( US_volume, tank_height)
        mqtt_ready = True

        if tank_height != None:
            led_tank_water_level(tank_height)

        filling = next_state(US_volume,filling)
        set_pump(filling)

        send_i2c()
        time.sleep(.5)
                                                #errorhandeling
    except RuntimeError:
        print("no measurement, retrying")
        set_pump(False)
        filling = False
        time.sleep(1)
        continue

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exception(e)
        set_pump(False)
        filling = False
