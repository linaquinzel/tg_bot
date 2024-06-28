from os import getenv
import logging
import sys
import datetime

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.redis import RedisStorage
import asyncio
from dotenv import load_dotenv
from redis import asyncio as aioredis
from dateutil import parser 

import src.keyboard as keyboard
import src.filter as filter
import src.middlewares as middlewares

load_dotenv()

TG_TOKEN = getenv('TG_TOKEN')
HOST_REDIS = getenv('HOST_REDIS')

PORT_REDIS = getenv('PORT_REDIS')
redis_client = aioredis.Redis(host=HOST_REDIS, port=PORT_REDIS, decode_responses=True)

dp = Dispatcher(storage=RedisStorage(redis=redis_client))

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """

    await redis_client.sadd('users', message.chat.id)
    await middlewares.set_cooldown(message, redis_client)
    if await middlewares.get_cooldown(message, redis_client):
        await message.answer(
            f"Hello, {html.bold(message.from_user.full_name)}!",
            reply_markup=keyboard.main_keyboard
        )
        await middlewares.set_cooldown(message, redis_client)


@dp.message(F.text.lower() == "подписаться на новое ус-во")
async def subscribe_handler(message: Message) -> None:
    """
    Хендлер кнопки вывода подсказки для подписки на новое устройство
    """
    if await middlewares.get_cooldown(message, redis_client):
        await message.reply(
            "Введите MAC-адрес устройства в формате '00:AB:CD:EF:11:22': ",
            reply_markup=keyboard.main_keyboard
        )
        await middlewares.set_cooldown(message, redis_client)

@dp.message(F.text.lower() == "отписаться от ус-ва")
async def unsubscribe_handler(message: Message) -> None:
    """
    Хендлер кнопки отписки от существующих подписок
    """
    active_subscribes = await redis_client.scan(
        match='subscribe '+str(message.chat.id)+'*'
    )
    set_topics = set()
    if active_subscribes[1]:
        for i in active_subscribes[1]:
            topic = i.split()[2]
            set_topics.add(topic)
            unsubscribe_keyboard = keyboard.get_inline_kb_unsubscribe(set_topics)
        if await middlewares.get_cooldown(message, redis_client):
            await middlewares.set_cooldown(message, redis_client)
            await message.answer(
                'Вот ссылки на отписку:',
                reply_markup=unsubscribe_keyboard
            )
    if not active_subscribes[1]:
        if await middlewares.get_cooldown(message, redis_client):
            await middlewares.set_cooldown(message, redis_client)
            await message.answer(
                'У вас нет активных подписок!',
                reply_markup=keyboard.main_keyboard
            )
    


@dp.message(F.text.func(filter.mac_address_check))
async def mac_address_handler(message: Message) -> None:
    """
    Хендлер подписки на устройство
    """
    topic = message.text
    # время жизни подписки - 5 минут
    await redis_client.set(
        name=f'subscribe {str(message.chat.id)} {topic}',
        value='0',
        ex=300
    )
    value = datetime.datetime.now().strftime("%Y-%m-%d") + ' ' + topic
    existing_subscribes = await redis_client.hget(
        'last_subscribes',
        str(message.chat.id)
    )
    try:
        existing_subscribes += ' ' + value
    except TypeError:
        existing_subscribes = value + ' '
    await redis_client.hset(
        name='last_subscribes',
        key=str(message.chat.id),
        value=existing_subscribes
    )
    if await middlewares.get_cooldown(message, redis_client):
        await message.reply(
            f"Вы успешно подписались на топик {message.text}",
            reply_markup=keyboard.main_keyboard
        )
        await middlewares.set_cooldown(message, redis_client)

@dp.callback_query(F.data.func(filter.mac_address_check))
async def mac_address_return_subscribe_handler(call: CallbackQuery) -> None:
    """
    Хендлер повторной подписки на устройство
    """
    topic = call.data
    await redis_client.set(
        name=f'subscribe {str(call.message.chat.id)} {topic}',
        value='0',
        ex=300
    )
    value = datetime.datetime.now().strftime("%Y-%m-%d") + ' ' + topic
    
    existing_subscribes = await redis_client.hget(
        'last_subscribes',
        str(call.message.chat.id)
    )
    try:
        existing_subscribes += ' ' + value
    except TypeError:
        existing_subscribes = value + ' '
    await redis_client.hset(
        name='last_subscribes',
        key=str(call.message.chat.id),
        value=existing_subscribes
    )
    if await middlewares.get_cooldown(call.message, redis_client):
        await call.message.reply(
            f"Вы успешно повторно подписались на топик {topic}",
            reply_markup=keyboard.main_keyboard
        )
        await middlewares.set_cooldown(call.message, redis_client)

@dp.callback_query(F.data.func(filter.unsubscribe_check))
async def mac_address_unsubscribe_handler(call: CallbackQuery) -> None:
    """
    Хендлер отписки от устройства
    """
    topic = call.data.split()[1]
    await redis_client.delete(
        'subscribe '+str(call.message.chat.id)+' '+topic
    )
    if await middlewares.get_cooldown(call.message, redis_client):
        await call.message.reply(
            f"Вы успешно отписались от топика {topic}",
            reply_markup=keyboard.main_keyboard
        )
        await middlewares.set_cooldown(call.message, redis_client)

@dp.message(F.text.lower() == "просмотр последних запрошенных ус-в")
async def last_subscribes_handler(message: Message) -> None:
    """
    Хендлер кнопки запроса списка последних подписок
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_dt = parser.parse(today)
    last_subscribes = []
    async for k in redis_client.hscan_iter(
        name='last_subscribes',
        match=str(message.chat.id)
    ):
        last_subscribes.append(list(k))
    active_subscribes = set()
    async for k in redis_client.scan_iter(match='subscribe '+ str(message.chat.id) + '*'):
        active_topic = k.split()[-1]
        active_subscribes.add(active_topic)
        if k in last_subscribes:
            last_subscribes.remove(k)
    set_topics = set()
    if last_subscribes:
        for i in last_subscribes:
            topic = i[1].split()
            for k in range(0, len(topic)):
                if k == 0 or k % 2 == 0:
                    date = topic[k]
                    dt = parser.parse(date)
                    if today_dt == dt:
                        if topic[k+1] not in active_subscribes:
                            set_topics.add(topic[k+1])
        last_subscribes_kb = keyboard.get_inline_kb_last_subscribes(set_topics)
        if set_topics and await middlewares.get_cooldown(message, redis_client):
            await middlewares.set_cooldown(message, redis_client)
            await message.answer(
                'Вот ссылки на подписку:',
                reply_markup=last_subscribes_kb
            )
        if not set_topics:
            if await middlewares.get_cooldown(message, redis_client):
                await middlewares.set_cooldown(message, redis_client)
                await message.answer(
                    'У вас нет неактивных подписок!',
                    reply_markup=keyboard.main_keyboard
                )
        
    else:
        if await middlewares.get_cooldown(message, redis_client):
            await middlewares.set_cooldown(message, redis_client)
            await message.answer(
                'У вас нет последних подписок!',
                reply_markup=keyboard.main_keyboard
            )

@dp.message()
async def errors_handler(message: Message):
    if await middlewares.get_cooldown(message, redis_client):
        await message.answer(
            "Вы совершили ошибку при вводе команды, попробуйте ещё раз!",
            reply_markup=keyboard.main_keyboard
        )
        await middlewares.set_cooldown(message, redis_client)

async def send_message(bot):
    """
    Собирает все накопившиеся сообщения из storage и рассылает по юзерам
    """
    subscribes = []
    async for k in redis_client.scan_iter(match='subscribe*'):
        subscribes.append(k)
    set_subscribers = set()
    set_topics = set()
    try:
        for i in subscribes:
            string = i.split()
            subscriber = string[1]
            topic = string[2]
            set_subscribers.add(subscriber)
            set_topics.add(topic)
    except KeyError:
        print('Пустой словарь')
    # словарь вида топик: все сообщения за последние три секунды
    goal = {} 
    try:
        for topic in set_topics:
            target = 'device/'+topic
            now_time = datetime.datetime.now()
            for j in range(3, 0, -1):
                match = (
                    now_time-datetime.timedelta(seconds=j)
                ).strftime("%Y-%m-%d %H:%M:%S")
                async for k in redis_client.hscan_iter(
                    name=target,
                    match=match+'*'
                ):
                    goal[topic] = k
    except KeyError:
        print('Пустой словарь 1')
    
    # сборка сообщений в один словарь вида юзер: сообщение
    final_message = {}
    try:
        for subs in set_subscribers:
            final_message[subs] = ''
            for i in subscribes:
                for topic in set_topics:
                    try:
                        if topic in i and subs in i:
                            existing_message = final_message[subs]
                            next_message = topic + ' отправил сообщение в ' + str(goal[topic][0]) + ' о том, что ' + str(goal[topic][1]) + '\n'
                            final_message[subs] = existing_message + next_message
                        elif topic not in i:
                            pass
                    except KeyError:
                        await asyncio.sleep(3)
                        await send_message(bot)
            if await middlewares.get_cooldown_by_user_id(subs, redis_client):
                await bot.send_message(
                    chat_id=subs,
                    text=final_message[subs][:4090],
                    reply_markup=keyboard.main_keyboard
                ) # нужно предусмотреть разбивку слишком длинных сообщений
                await middlewares.set_cooldown_by_user_id(subs, redis_client)
    except KeyError:
        print('Пустой словарь 2')
    
    while True:
        await asyncio.sleep(3)
        await send_message(bot)



async def main() -> None:
    bot = Bot(
        token=TG_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    future = asyncio.ensure_future(send_message(bot))
    await dp.start_polling(bot)
    future.cancel()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.get_event_loop().run_until_complete(main())