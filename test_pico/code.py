import time
import board
import digitalio
import os
import wifi
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_hcsr04

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP14, echo_pin=board.GP15)
#pomp pins defenitie
pump = digitalio.DigitalInOut(board.GP0)
pump.direction = digitalio.Direction.OUTPUT

# laagste punt van het glas(of vanaf waar hij moet beginnen met vullen) in cm
start_fill = 30
# punt vanaf waar hij moet stoppen met vullen in cm
stop_fill = 105
#interval en laatste poging om connectie te maken met wifi
connectie_interval = 10
laatste_poging = -connectie_interval    #initialisatie is -interval zodat hij connectie probeert te maken vanaf het moment dat hij gepowered word

#geeft waarde terug of pomp moet aanslaan of niet
def set_pump(on_off):
    pump.value = on_off


def next_state(distance, filling):
    if not filling and distance > start_fill:
        return True
    if filling and distance < stop_fill:
        return False
    
    #behoud de stand van de pomp als de status niet moet veranderen
    return filling



def Wifi_connection():
    global laatste_poging               #global = variabele die buiten deze functie zich bevind, anders maakt hij er een nieuwe van
    if wifi.radio.connected:
        return

    if time.monotonic() -laatste_poging < connectie_interval:   #time.monotonic is een klok die enkel opteld -> goed om tijdsverschillen in een programma te meten
        return
    
    laatste_poging = time.monotonic()       # moet voor de try anders voert die enkel uit bij een succes
    try:
        print("connecting to wifi")
        wifi.radio.connect(os.getenv("WIFI_SSID"),os.getenv("WIFI_PASSWORD"),timeout= 10)   #timeout op 10 gezet, met 3 begonnen maar was te kort.
        print(f"connected to wifi as {wifi.radio.ipv4_address}")
    except(ConnectionError, TimeoutError) as e:
        print("error",e)

                                                                    #connection variables
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

                                                                    #connection part mqtt

def connect_mqtt():
    print("connect_mqtt started")
    if not wifi.radio.connected:
        print("wifi not connected")
        return
    if mqtt_client._is_connected:
        print("mqtt already connected")
        return
    try:
        print("connecting to mqtt")
        mqtt_client.connect()
        print("mqtt connection succesfull")
    except Exception as e:
        print(f"mqtt error: {e}")

CHAN_ID = os.getenv("CHAN_ID")
PUBLISH_TOPIC = f"channels/{CHAN_ID}/publish"

publish_interval = 20
vorige_publish = time.monotonic()

                                                                    #publish part mqtt

def publish_mqtt(distance,filling):
    global vorige_publish
    if time.monotonic() - vorige_publish > publish_interval:
        vorige_publish = time.monotonic()
        payload = f"field1={distance:.1f}&field2={1 if filling else 0}"
        try:
            mqtt_client.publish(PUBLISH_TOPIC, payload)
            print("published:", payload)
        except Exception as e:
            print("mqtt publish error:", e)
            try:
                mqtt_client.disconnect()
            except Exception:
                pass




filling = False
set_pump(filling)

while True:

    if not filling:
        Wifi_connection()
    if wifi.radio.connected and not mqtt_client.is_connected():
        print(mqtt_client._is_connected)
        connect_mqtt()

        
    try:
        #haalt de stand van het water op
        distance = sonar.distance
    except RuntimeError:
        print("no echo, retrying")
        set_pump(False)
        filling = False
        time.sleep(1)
        continue

    #checked of hij bij moet worden gevuld
    filling = next_state(distance, filling)
    set_pump(filling)

    if mqtt_client.is_connected():
        publish_mqtt(distance, filling)

    #debug print
    print(f"distance: {distance:.1f} cm  filling: {filling}")
    time.sleep(1)