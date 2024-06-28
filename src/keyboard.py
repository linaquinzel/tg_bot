from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Подписаться на новое ус-во"),
            KeyboardButton(text="Отписаться от ус-ва"),
            
        ],
        [
            KeyboardButton(text="Просмотр последних запрошенных ус-в"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие: ",
    one_time_keyboard=True,
)
def get_inline_kb_unsubscribe(topics):
    inline_kb_list = []
    for topic in topics:
        inline_kb_list.append([InlineKeyboardButton(text=topic, callback_data='unsubscribe '+topic)])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def get_inline_kb_last_subscribes(topics):
    inline_kb_list = []
    for topic in topics:
        inline_kb_list.append([InlineKeyboardButton(text='Подписаться на '+str(topic), callback_data=str(topic))])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

delete_keyboard = ReplyKeyboardRemove()