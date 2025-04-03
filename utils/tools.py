from datetime import datetime
import logging
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from dataclasses import dataclass
from aiogram.utils import markdown
from utils.inputing import bot
import pytz
from utils.lists_or_dict import admin_ru

from data.sqltables import BotChatINFO, MePayments, User
logger = logging.getLogger(__name__)

def date_moscow(option: str) -> int | str:
    moscow_time = pytz.timezone('Europe/Moscow')
    if option == 'date':
        time = datetime.now(moscow_time).date()
    elif option == 'time_info':
        time = datetime.now(moscow_time).strftime(
            f"Дата: {markdown.hbold(f'%d.%m.%Y')}\n"
            f"Время: {markdown.hbold('%H:%M')}"
            )
    elif option == 'time_and_date':
        time = datetime.now(moscow_time).strftime(f'%d.%m.%Y''%H:%M')
    elif option == 'time_now':
        time = datetime.now(moscow_time)
    else:
        raise ValueError('Такого объекта не представленно в функции.')
    return time

async def user_changes_data(db_session: AsyncSession, cls, params: dict[str, Any]):
    try:
        user_id = params.get('user_id')
        
        if user_id:
            base = await db_session.execute(select(cls).where(cls.user_id == user_id))
            copy_table = base.scalars().one_or_none()
            if copy_table:
                update = Update_date(
                    base=copy_table,
                    params=params
                )
                await update.save_(db_session)
                return copy_table
            else:
                tab = cls(**params)    
                db_session.add(tab)
                await db_session.commit()
                logger.info(f'Добавлен новый юзер в таблицу {cls.__name__}')  
                return tab
        else:
            logger.error(f'user_id не передан в словаре: {params}')
            return None
    except Exception as e:
        logger.error(f'Ошибка в функции user_changes_data: {e}')
        return None

class GetInfo:
    def __init__(self, chat_id: int, db_session: AsyncSession):
        self.chat_id = chat_id
        self.db_session = db_session
        
    async def get_chat_admins(self):
        admins = await bot.get_chat_administrators(self.chat_id)
        return [admin.user.id for admin in admins if not admins.user.is_bot]

    async def get_chat_creator(self):
        admins = await bot.get_chat_administrators(self.chat_id)
        for admin in admins:
            if admin.status in admin_ru:  # Статус создателя
                return admin.user.id
        return None
    
    async def get_chat_members(self):
        member = await bot.get_chat_member(self.chat_id)
        count_member = await bot.get_chat_member_count(self.chat_id)     

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

@dataclass
class BasicUser:
    user_id: int
    full_name: str
    user_name: str | None

    @classmethod
    def from_message(cls, message: Message):
        return cls(
            user_id=message.from_user.id,
            full_name=message.from_user.full_name if len(message.from_user.full_name) <= 30 else message.from_user.full_name[:10].join('...'),
            user_name=message.from_user.username if message.from_user.username else "Без него",
        )
