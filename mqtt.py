import paho.mqtt.client as mqtt
import time
from random import randint
broker = 'broker.emqx.io'
port = 1883
topic = "house"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt.Client()

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish_msg():
    print('Message Published')

client = connect_mqtt()
while True:
    client.on_publish = publish_msg()

    ret = client.publish('house', 'on')

    client.loop()
    sleeptime = randint(1, 5)
    print("sleeping for:", sleeptime, "seconds")
    time.sleep(sleeptime)
    print("sleeping is over")

    ret1 = client.publish('house', 'off')