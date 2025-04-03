import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, CallbackQuery 
import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from commands.states.state import panell, stars_count
from config import env_import
from data.sqltables import MePayments, User
from keyborads.button_class.root_classes import Help_Commands
from keyborads.inline import commands_help_admin, dash_panel, pay_stars
from utils.tools import Update_date
from utils.inputing import __env__
from utils.inputing import bot
from keyborads.inline import help_callback
from utils.lists_or_dict import help_class

router = Router(name=__name__)
logger = logging.getLogger(__name__)
log = '❌ Не найдены данные кнопки'

@router.callback_query(help_callback.filter())
async def create_buttons(call: CallbackQuery, calldata: dict):
    try:
        select_command = calldata['command']
        logger.info(f'Выбранная кнопка с data: {select_command if select_command is not None else log}')
        description = help_class.get(select_command, log)
    
        await call.message.answer(description)
    except Exception as e:
        logger.info(f'Ошибка в функции create_buttons: {e}')
        

