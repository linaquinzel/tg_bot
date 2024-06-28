from __future__ import annotations
import time

import asyncio

async def get_cooldown(message, redis_client):
    user_cooldown = await redis_client.hget('users_time_cutoff', str(message.chat.id))
    bot_cooldown = await redis_client.get('bot_time_cutoff')
    try:
        if float(user_cooldown) > time.time(): 

            print(float(user_cooldown)-time.time())
            await asyncio.sleep(float(user_cooldown)-time.time())

            if float(bot_cooldown) > time.time():

                print(float(bot_cooldown)-time.time())
                await asyncio.sleep(float(bot_cooldown)-time.time())
                return True
            
            return True
    except TypeError:
        return True
    return True

async def get_cooldown_by_user_id(user_id, redis_client):
    user_cooldown = await redis_client.hget('users_time_cutoff', str(user_id))
    bot_cooldown = await redis_client.get('bot_time_cutoff')
    try:
        if float(user_cooldown) > time.time(): 

            print(float(user_cooldown)-time.time())
            await asyncio.sleep(float(user_cooldown)-time.time())

            if float(bot_cooldown) > time.time():

                print(float(bot_cooldown)-time.time())
                await asyncio.sleep(float(bot_cooldown)-time.time())
                return True
            
            return True
    except TypeError:
        return True
    return True



async def set_cooldown(message, redis_client):
    now = time.time()
    time_cutoff_for_user = now + 3
    time_cutoff_for_bot = now + 0.33
    await redis_client.hset('users_time_cutoff', str(message.chat.id), str(time_cutoff_for_user))
    await redis_client.set('bot_time_cutoff', str(time_cutoff_for_bot))



async def set_cooldown_by_user_id(user_id, redis_client):
    now = time.time()
    time_cutoff_for_user = now + 3
    time_cutoff_for_bot = now + 0.33
    await redis_client.hset('users_time_cutoff', str(user_id), str(time_cutoff_for_user))
    await redis_client.set('bot_time_cutoff', str(time_cutoff_for_bot))