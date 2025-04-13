import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, Depends
from aiogram import Dispatcher, Router, Bot
import logging
from aiogram.types import Update
from data.middlew import CheckNotMessage, DatabaseMiddleware
from data.sqltables import create_tables
from utils.inputing import bot, dp
from data.sqltables import async_session
from config import __env__


ask = input('Запуск с telethon? yes/no:')
router = Router(name=__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
setup_webhook = __env__('LOCALHOST_WEBHOOK')

def create_lifespan(bot: Bot):
    if '/webhook' in setup_webhook:
        webhooki = setup_webhook
    else:
        webhooki = setup_webhook + '/webhook'   
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != webhooki:
            logger.info("Bot started...")
            await bot.set_webhook(webhooki)
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
    dp.message.middleware(CheckNotMessage())
    await dp.feed_update(bot, update)
    return {'status': 'ok'}


if __name__ == "__main__":
    uvicorn.run(app, host=__env__('LOCALHOST_WEBHOOK_HOST'), port=__env__('LOCALHOST_WEBHOOK_PORT'))