import paho.mqtt.client as mqtt
import time
from random import randint, choice
from os import getenv
from dotenv import load_dotenv

load_dotenv()

PORT_MQTT = int(getenv('PORT_MQTT'))
HOST_MQTT = getenv('HOST_MQTT')

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    client.connect(HOST_MQTT, PORT_MQTT)
    return client

def publish_msg():
    print('Message Published')

client = connect_mqtt()
while True:
    client.on_publish = publish_msg()
    foo = ['a', 'b', 'c', 'd', 'e', 1, 2, 3, 4, 5, 6]
    ret = client.publish('device/00:6A:B6:6B:BA:7A', 'on '+str(choice(foo)))

    sleeptime = randint(1, 2)
    print("sleeping for:", 1, "seconds")
    time.sleep(1)
    print("sleeping is over")

    ret1 = client.publish('device/00:50:B6:5B:CA:6A', str('off '+str(choice(foo))))

    client.loop()