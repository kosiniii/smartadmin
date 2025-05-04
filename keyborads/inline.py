import logging
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from keyborads.root_classes import Help_Settings, Data
from utils.inputing import __env__
from utils.lists_or_dict import help_class
from aiogram.types import CallbackData


logger = logging.getLogger(__name__)
MAIN_BOT_USERNAME = __env__('MAIN_BOT_USERNAME')
help_callback = CallbackData("help", "command")
builder = InlineKeyboardBuilder()

def dash_panel(data: Data):
    builder.button(
        text='📃 Дока о боте ',
        url=f"https://github.com/kosiniii/{__env__('PROJECT_ON_GITHUB')}"
    )
    builder.button(
        text='➕ Добавить в чат',
        url=f"https://t.me/{MAIN_BOT_USERNAME}?startgroup=true"
        )
    builder.button(
        text='⚙ Настроить бота',
        callback_data=data.settings
    )
    builder.adjust(1, 2)
    return builder.as_markup(resize_keyboard=True)

def pay_stars(stars: int):
    builder.button(
        text=f'{stars} к оплате',
        pay=True
        )
    return builder.as_markup(resize_keyboard=True)

def commands_help_admin():
    try:
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
    
def app_button():
    builder.button(
        text='📱 Запустить приложение',
        url=f"{__env__('DIRECT_LINK_APP')}"
    )
    builder.adjust(1)
    return builder.as_markup()
    