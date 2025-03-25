import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, Depends
from aiogram import Dispatcher, Router, Bot
import logging
from aiogram.enums import ParseMode
from aiogram.loggers import webhook
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.client.bot import DefaultBotProperties
from config import env_import
from data.middlew import DatabaseMiddleware
from data.sqltables import create_tables
from utils.inputing import __env__
from data.sqltables import async_session

router = Router(name=__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
dp = Dispatcher()
bot = Bot(
    token=__env__('MAIN_BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
logging.basicConfig(level=logging.INFO)


def create_lifespan(bot: Bot):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != __env__('LOCALHOST_WEBHOOK'):
            logger.info("Bot started...")
            await bot.set_webhook(__env__('LOCALHOST_WEBHOOK'))
        asyncio.run(create_tables())
            
        yield
        logger.info("Bot stopped...")
        await bot.delete_webhook()
    return lifespan

app = FastAPI(lifespan=create_lifespan(bot))

@app.post('/webhook')
async def bot_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    dp.update.middleware(DatabaseMiddleware(async_session))
    await dp.feed_update(bot, update)
    return {'status': 'ok'}


if __name__ == "__main__":
    uvicorn.run(app, host=__env__('LOCALHOST_WEBHOOK_HOST'), port=__env__('LOCALHOST_WEBHOOK_PORT'))