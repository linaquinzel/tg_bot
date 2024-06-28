import paho.mqtt.client as mqtt

from dotenv import load_dotenv
from os import getenv
from datetime import datetime
import redis
from redis import asyncio as aioredis
import asyncio

load_dotenv()

PORT_MQTT = int(getenv('PORT_MQTT'))
HOST_MQTT = getenv('HOST_MQTT')
HOST_REDIS = getenv('HOST_REDIS')

PORT_REDIS = getenv('PORT_REDIS')
# async def connect_redis():
#     global redis_client
#     redis_client = aioredis.Redis(host=HOST_REDIS, port=PORT_REDIS, decode_responses=True)
redis_client = redis.Redis(host=HOST_REDIS, port=PORT_REDIS, decode_responses=True)

def process_message(client, userdata, message):
    # print(str(message.topic), str(time.time()), str(message.payload.decode('utf-8')))
    time = str(datetime.now())
    redis_client.hset(
        name=str(message.topic),
        key=time,
        value=str(message.payload.decode('utf-8'))
    )

    


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(reason_code_list[0])
        reason_code = reason_code_list[0]
    else:
        print(reason_code_list[0].value)
        reason_code = reason_code_list[0].value
    print(reason_code)

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")

async def connect_mqtt():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    client.connect(host=HOST_MQTT, port=PORT_MQTT)

    client.on_message = process_message

    client.subscribe('device/#')
    print('subscribed')
    client.loop_forever()

async def main():
    while True:
        # await connect_redis()
        await connect_mqtt()

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
