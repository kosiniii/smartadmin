from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from utils.tools import date_moscow
from config import __env__


bot = Bot(
    token=__env__('MAIN_BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
dp = Dispatcher()



