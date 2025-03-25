import asyncio
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, CallbackQuery, Message, ReplyKeyboardRemove
import logging
import random
import redis
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from commands.states.state import panell
from config import env_import
from data.sqltables import User
from keyborads.lists_buttons import dash_panel_list
from keyborads.buttons import dash_panel
from utils.tools import BasicUser, Update_date

logger = logging.getLogger(__name__)

router = Router(name=__name__)

@router.message(Command(commands='start', prefix='/'))
async def starting(message: Message):
    await message.answer(
        text='🚀 Я бот администратор.\n'
        'Добавь меня вы чат скорее !!!',
        reply_markup=dash_panel()
        )
    

@router.message(Command.commands['/start', '/info'])  
async def commands_add(message: Message, db_session: AsyncSession):
    user = BasicUser.from_message(message)
    
    ADMIN_ID = env_import('ADMIN_ID')
    full_name = user.full_name
    user_id = user.user_id
    user_name = user.user_name
    admin_status = 'user'
    
    if isinstance(ADMIN_ID, int) and ' ' not in ADMIN_ID:
        if user_id == env_import('ADMIN_ID'):
            admin_status = 'admin'
    else:
        for ids in ADMIN_ID:
            if ids == user_id:
                admin_status = 'admin'
    
    base = await db_session.execute(select(User).where(User.user_id == user_id))
    result_base = base.scalars().one_or_none()
    if result_base:
        update = Update_date(
            base=result_base,
            params={
                'user_id': user_id,
                'user_name': user_name,
                'full_name': full_name,
                'admin_status': admin_status
            }
        )
        await update.save_(db_session)
    else:
        user = User(
            user_id = user_id,
            user_name = user_name,
            full_name = full_name,
            admin_status = admin_status
        )
        await db_session.add(user)
        db_session.commit()
        logger.info(f'Пользователь добавлен в бд\n id: {user_id}')


