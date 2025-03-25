from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from utils.inputing import __env__


MAIN_BOT_USERNAME = __env__('MAIN_BOT_USERNAME')
def dash_panel():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Добавить меня в чатик 💋',
        url=f"https://t.me/{MAIN_BOT_USERNAME}?startgroup=true"
        )
    builder.button(
        text='Дока о боте 📃',
        url=f"https://github.com/kosiniii/{__env__('PROJECT_ON_GITHUB')}"
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)