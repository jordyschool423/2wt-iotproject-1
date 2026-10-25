import os
import time
import threading
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

import oled


load_dotenv()

# --- Setup ---
HOST = os.getenv("MQTT_HOST")
PORT = 8883
CLIENT_ID = os.getenv("MQTT_CLIENT_ID")
USERNAME = os.getenv("MQTT_UNAME")
PASSWORD = os.getenv("MQTT_PASSWD")
TOPIC = os.getenv("MQTT_TOPIC")

# Shared global state (written by the MQTT thread, read by the main thread)
last_message = None


# --- MQTT callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected, result:", reason_code)
    client.subscribe(TOPIC)


def on_message(client, userdata, message):
    global last_message
    last_message = message.payload.decode()
    print(f"Received on {message.topic}: {last_message}")


# --- MQTT client ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message


# --- Thread task ---
def task_mqtt():
    """Keeps listening for MQTT messages (also reconnects if the connection drops)."""
    print("MQTT thread started.")
    client.loop_forever()
    print("MQTT thread stopped.")


# --- Main Execution ---
client.connect(HOST, PORT)

t1 = threading.Thread(target=task_mqtt, daemon=True)
print("Starting threads...")
t1.start()

try:
    counter = 0
    while True:
        # Main thread is free for other logic (sensors, LEDs, ...)
        print(f"Main thread heart beat: {counter}, last message: {last_message}")
        counter += 1
        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    client.disconnect()  # makes loop_forever() return
    t1.join()            # wait for the thread to finish
    print("Done.")