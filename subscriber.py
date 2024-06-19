import paho.mqtt.client as mqtt

def process_message(client, userdata, message):
    print('Message received: ', str(message.payload.decode('utf-8')))
    print('Message topic: ', message.topic)
    print('Message qos: ', message.qos)
    print('Message retain flag: ', message.retain)

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

client.on_message = process_message

client.connect('broker.emqx.io', 1883, 60)

client.subscribe('house')

client.loop_forever()