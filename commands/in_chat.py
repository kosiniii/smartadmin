import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, CallbackQuery, Message, LabeledPrice, PreCheckoutQuery, ChatJoinRequest
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
from keyborads.inline import dash_panel, pay_stars
from utils.tools import Update_date
from utils.inputing import bot, __mute_users__, __ban_users__, __env__

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.chat_join_request()
async def joing_to_chat(update: ChatJoinRequest):
    chat_id = update.chat.id