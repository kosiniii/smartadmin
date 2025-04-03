import logging
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from keyborads.button_class.root_classes import Help_Settings
from utils.inputing import __env__
from utils.lists_or_dict import help_class
from aiogram.types import CallbackData


logger = logging.getLogger(__name__)
MAIN_BOT_USERNAME = __env__('MAIN_BOT_USERNAME')
help_callback = CallbackData("help", "command")


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

def pay_stars(stars: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Оплатить {stars} ⭐️',
        pay=True
        )
    return builder.as_markup(resize_keyboard=True)

def commands_help_admin():
    try:
        builder = InlineKeyboardBuilder()
        sum_buttons = 1
        for command in help_class.keys():
            builder.button(
                text=command,
                callback_data=help_callback.new(command=command)
            )
        if len(help_class) // 10 > 0:
            sum_buttons += 1
        builder.adjust(sum_buttons)
        return builder.as_markup(resize_keyboard=True)
    
    except Exception as e:
        logger.error(
            '❗ Не создалась inline функция с callback_data ❗\n'
            f'Причина: \n{e}'
            )
        return None
    