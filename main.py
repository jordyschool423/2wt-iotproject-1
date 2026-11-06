import os
import time
import threading
import json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from camera import get_animal                                                                  #import om foto te maken en terug te sturen wat er aan het drinken is
from oled import refresh_display, refresh_display_drinking, show_message, turn_off_display    #imports functie om oled aan te sturen

load_dotenv()

# --- Setup ---
HOST = os.getenv("MQTT_HOST")
PORT = 8883
CLIENT_ID = os.getenv("MQTT_CLIENT_ID")
USERNAME = os.getenv("MQTT_UNAME")
PASSWORD = os.getenv("MQTT_PASSWD")
TOPIC = os.getenv("MQTT_TOPIC").split(",")

# Shared global state (written by the MQTT thread, read by the main thread)
field1 = None
field2 = None


# --- MQTT callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected, result:", reason_code)
    for topic in TOPIC:
        print("Subscribing to:", repr(topic))
        client.subscribe(topic)


def on_message(client, userdata, message):
    global field1, field2
    data = json.loads(message.payload.decode())
    field1 = data.get("field1")
    field2 = data.get("field2")
    print("field1:", field1, "| field2:", field2)
    refresh_display(field1)
    return (field1)
    


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print("Subscribe result:", reason_code_list)


# --- MQTT client ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe


# --- Thread task ---
def task_mqtt():
    """Keeps listening for MQTT messages (also reconnects if the connection drops)."""
    print("MQTT thread started.")
    client.loop_forever()
    print("MQTT thread stopped.")


# --- Main Execution ---
show_message("loading data")
client.connect(HOST, PORT)

t1 = threading.Thread(target=task_mqtt, daemon=True)
print("Starting threads...")
t1.start()

waterlevel = field1

try:
    counter = 0
    while True:
        # Main thread is free for other logic (sensors, LEDs, ...)
        print(f"Main thread heart beat: {counter}, last message: {field1, field2}")
        counter += 1

        if waterlevel > 200:
            animal = get_animal()
            refresh_display_drinking(f"{animal} is drinking")
        









        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    client.disconnect()     # makes loop_forever() return
    t1.join()               # wait for the thread to finish
    turn_off_display()      #shutdown of the oled       
    print("Done.")