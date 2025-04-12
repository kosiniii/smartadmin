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
from utils.tools import GetInfoChat, Update_date
from utils.inputing import bot, __mute_users__, __ban_users__, __env__
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=True))
async def bot_added(event: ChatMemberUpdated, db_session: AsyncSession):
    chat = event.chat
    chat_id = chat.id
    chat_username = chat.username
    chat_title = chat.title if chat.title else chat_username
        
    if event.new_chat_member.user.id == bot.id:
        inviter = event.from_user
        gic = GetInfoChat(chat_id, db_session, inviter.id)
        
        await bot.send_message(__env__('ADMIN_ID'), f"➡️ {markdown.hlink('Чел', f'tg://user?id={inviter.id}')} пригласил бота в чат {chat.title} ⬅️")
        await bot.send_message(inviter.id, f'Спасибо что пригласили в чатик -> {markdown.hcode(chat_title)} 🤗')
        
        if await gic.save_to_db_data(chat_username):
            logger.info('Все данные с чата УСПЕШНО! загруженны в бд')
        else:
            logger.debug('ВНИМАНИЕ! не все данные были загруженны в бд')

@router.chat_join_request()
async def joing_to_chat(event: ChatMemberUpdated, db_session: AsyncSession):
    pass
        