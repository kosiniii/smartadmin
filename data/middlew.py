import asyncio
import logging
from aiogram import BaseMiddleware
from sqlalchemy import select, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.types import TelegramObject, CallbackQuery, Message, LabeledPrice, PreCheckoutQuery, ChatJoinRequest, ChatMemberUpdated
logger = logging.getLogger(__name__)
base = BaseMiddleware()

class DatabaseMiddleware(base):
    def __init__(self, session_factory: async_sessionmaker):
        super().__init__()
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            data["db_session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при обработке запроса: {e}")
                    

class CheckNotMessage(BaseMiddleware):
    async def on_process_message(self, message: Message, data: Dict[str, Any]):
        if message.from_user.is_bot or message.from_user.username.endswith("bot"):
            return False 

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        result = await handler(event, data)
        return result