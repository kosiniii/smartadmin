import asyncio
import logging
import random
from typing import Any, Dict, Optional, Type
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from dataclasses import dataclass
from aiogram.utils import markdown
import pytz
from aiogram.types import ChatMemberUpdated, Chat
from utils.lists_or_dict import admin_ru
from utils.inputing import dp, bot
from data.sqltables import BotChatINFO, ChatCache, ChatMember, MePayments, User
from sqlalchemy.orm import DeclarativeMeta
from utils.date import DateMoscow, date_moscow
logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, db_session: AsyncSession):
        self.dao = BaseDAO(MePayments, db_session)

    async def add_or_update_payment(self, user_id: int, amount: float):
        try:
            existing = await self.dao.get_one(MePayments.user_id == user_id)
            if existing:
                new_stars = existing.donated_stars + amount
                new_count = existing.payment_count + 1
                await self.dao.update(
                    MePayments.user_id == user_id,
                    {
                        'donated_stars': new_stars,
                        'payment_count': new_count,
                    }
                )
                return {
                    "date": date_moscow('time_and_date'),
                    "donated_stars": new_stars,
                    "payment_count": new_count,
                }
            else:
                await self.dao.create({
                    "user_id": user_id,
                    "donated_stars": amount,
                    "payment_count": 1,
                })
                return {
                    "date": date_moscow('time_and_date'),
                    "donated_stars": amount,
                    "payment_count": 1,
                }
        except Exception as e:
            logger.error(f"[PaymentService] Ошибка при добавлении оплаты: {e}")
            return None


class BaseDAO:
    def __init__(self, model: Type[DeclarativeMeta], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get_one(self, where: ColumnElement) -> Optional[DeclarativeMeta]:
        try:
            result = await self.db_session.execute(select(self.model).where(where))
            return result.scalars().one_or_none()
        except Exception as e:
            logger.error(f'DAO Ошибка: {e}')
            return None

    async def create(self, data: Dict[str, Any]) -> Optional[DeclarativeMeta]:
        try:
            obj = self.model(**data)
            self.db_session.add(obj)
            await self.db_session.commit()
            logger.info('DAO добавлено в базу')
            return obj
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f'DAO Ошибка: {e}')
            return None

    async def update(self, where: ColumnElement, data: Dict[str, Any]) -> bool:
        exiting = await self.get_one(where)
        if not exiting:
            logger.warning(f'DAO Объект не найден для обновления по: {where}')
            return False
                
        try:
            update = Update_date(
                base=self.get_one(),
                params=data
            )
            await update.save_(self.db_session)
            return True
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f'DAO Ошибка: {e}')
            return False
            
            
class GetInfoChat:
    def __init__(self, chat_id: int, db_session: AsyncSession):
        self.chat_id = chat_id
        self.db_session = db_session
        self.dao = BaseDAO(BotChatINFO, self.db_session)
        self.inviter_id = 0
    
    async def __call__(self):
        add_chat = BotChatINFO(
            chat_id = self.chat_id
        )
        self.db_session.add(add_chat)
        await self.db_session.commit()
        return add_chat
    
    async def get_inviter_id(self) -> int:
        if self.inviter_id != 0 and len(str(self.inviter_id)) >= 9:
            return self.inviter_id
        return 0
    
    async def get_count_members(self) -> int:
        count = bot.get_chat_member_count()
        if count:
            return count
        return 0
    
    async def get_chat_username(self):
        chat: Chat = await bot.get_chat(self.chat_id)
    
        if chat.username:
            return chat.username
        else:
            return "Not user"
    
    async def save_to_db_data(self):
        try:
            text_log = ''
            date = date_moscow(option='time_and_date')
            inviter_id = await self.get_inviter_id()
            count_members = await self.get_count_members()
            chat_username = await self.get_chat_username()

            data_BCI = {
                'chat_id': self.chat_id,
                'chat_username': chat_username,
                'inviter_id': inviter_id, 
                'count_members': count_members,
                'joing_bot_at': date
            }
            
            missing_data = []
            if count_members == 0:
                missing_data.append('count_members')
            if inviter_id == 0:
                missing_data.append('inviter_id')
                
            if missing_data:
                text_log = ', '.join(missing_data)
                warning_log = (
                    f'ПРЕДУПРИЖДЕНИЕ! Не хватает данных: {text_log}.\n'
                    f'count_members: {count_members}\ninviter_id: {inviter_id}\n'
                )
                logger.warning(warning_log)
                
            BCI_dao = self.dao.create({data_BCI})
            if BCI_dao:
                return True
            return False

        except Exception as e:
            logger.error(f'Ошибка в классе {__class__.__name__}, в модуле save_to_db_data:\n {e}')
            await self.db_session.rollback()
            return False
    
class GetMembersIds:
    def __init__(self, chat_username: str, count: int, chat_id: int):
        self.chat_username = chat_username
        self.count = count
        self.chat_id = chat_id
        
class Update_date:
    def __init__(self, base, params: dict[str, Any]):
        self.base = base
        self.params = params
        self.changes = {}
    
    def update(self) -> dict[str, tuple[str | int]]:
        try:
            for key, items in self.params.items():
                if hasattr(self.base, key):
                    old = getattr(self.base, key)
                    if old != items:
                        setattr(self.base, key, items)
                        self.changes[key] = [old, items]
                else:
                    logger.error(f"Не найден атрибут '{key}' в объекте {self.base.__class__.__name__}")
            if self.changes:
                user_id = self.params.get('user_id', 'не передано')
                logger.info(
                    f"Обновление пользователя {user_id}: "
                    f"Изменены поля: {list(self.changes.keys())}"
                )
            return self.changes
            
        except Exception as e:
            logger.error(
                f'Ошибка в классе: {__class__.__name__} в функции update\n'
                f'Причина: {e}'
                )
            raise
    
    async def save_(self, db_session: AsyncSession) -> bool:
        try:
            changes = self.update()
            if not changes:
                logger.info('Нет изменений.')
                return True

            db_session.add(self.base)
            await db_session.commit()
            return True
            
        except Exception as e:
            logger.error(f'Ошибка при сохранении в бд: {e}')
            await db_session.rollback()
            return False

class WelcomeUser:
    def __init__(self, event: ChatMemberUpdated , user_id: int, chat_id: int):
        self.date = DateMoscow('time_and_date_str')
        self.event = event
        self.user_id = user_id
        self.chat_id = chat_id
        self.bool: bool = False
        self.find_chat = None
    
    async def inject(self, db_session: AsyncSession):
        pass
        
        
#__user_warns__
# __user_message__
# __new_user__
# __mute_users__
# __ban_users__
class TimeCheduler:
    def __init__(self, date: int | str, chat_id: int, db_session: AsyncSession):
        self.date = date
        self.chat_id = chat_id
        self.db_session = db_session
        self.dao = BaseDAO(ChatMember, self.db_session)
    
    async def add_new_data(self):
        log_text = ''
        try:
            data = __new_user__.get_cashed()
            if data:
                chat_id: dict = data.get(self.chat_id, 'Не найден такой чат')
                for user_id in chat_id.keys():
                    exiting = await self.dao.create({
                        'user_id': user_id,
                        'chat_id': self.chat_id
                        })
                    if exiting:
                        continue
                    else:
                        logger.warning(
                            f'Ошибка в цикле в классе {__class__.__name__}\n'
                            f'Не удалось добавить юзера в бд: {user_id}'
                            )
                log_text = 'ВСЕ юзеры были добавленны в базу.'
                logger.info(log_text)
            else:
                log_text = (
                    'Бот не получил ни каких данных с __new_user__\n'
                    'Юзеры не были добавлены в базу.'
                    ) 
                logger.warning(log_text)
            return log_text
            
        except Exception as e:
            logger.error(f'Ошибка в {__class__.__name__}: {e}')
            return False
                 
    async def tree_hours(self):
        result = await self.add_new_data()
        if not result:
            result = '❌ ОШИБКА в TimeCheduler.add_new_data'
            
        await bot.send_message(self.chat_id, result)

    
