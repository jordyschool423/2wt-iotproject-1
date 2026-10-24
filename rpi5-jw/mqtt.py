import board
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

def on_connect(client, userdata, flags, rc, properties):
    if rc==0:
        print("Connected OK with result code "+str(rc))
    else:
        print("Bad connection with result code "+str(rc))

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))

def on_message(client,userdata,msg):
    print("Received a message on topic: " + msg.topic + "; message: " + msg.payload)



# Set up a MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, MQTT_CLIENT_ID)
client.username_pw_set(MQTT_USER, MQTT_PWD)


# Connect callback handlers to client
client.on_connect= on_connect
client.on_disconnect= on_disconnect
client.on_message= on_message

21
print("Attempting to connect to %s" % )
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_start() #start the loop