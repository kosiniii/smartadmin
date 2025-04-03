from aiogram import Bot
from config import env_import
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from data.redisetup import RedisBase
from utils.tools import date_moscow

__mute_users__ = RedisBase('mute_users', dict)
__ban_users__ = RedisBase('ban_users', dict)


__env__ = env_import
bot = Bot(
    token=__env__('MAIN_BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

create_date = date_moscow('time_and_date')


