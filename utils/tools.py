import asyncio
from datetime import datetime
import logging
from typing import Any, Dict, Optional, Type
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from dataclasses import dataclass
from aiogram.utils import markdown
from telethon_core.utils import collect_user_ids
from utils.inputing import bot
import pytz
from aiogram.types import TelegramObject, CallbackQuery, Message, LabeledPrice, PreCheckoutQuery, ChatJoinRequest, ChatMemberUpdated
from utils.lists_or_dict import admin_ru
from utils.inputing import dp, __env__, multi, __new_user__, create_date
from data.sqltables import BotChatINFO, ChatCache, ChatMember, MePayments, User
from sqlalchemy.orm import DeclarativeMeta
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
    
    async def get_chat_admins(self) -> list:
        admins = await bot.get_chat_administrators(self.chat_id)
        return [admin.user.id for admin in admins if not admins.user.is_bot]

    async def get_chat_creator(self) -> int:
        admins = await bot.get_chat_administrators(self.chat_id)
        for admin in admins:
            if admin.status in admin_ru:
                return admin.user.id
        logger.info(f'Не найден владелец чата {self.chat_id}')
        return 0
    
    async def get_count_members(self) -> int:
        count = bot.get_chat_member_count()
        if count:
            return count
        return 0
    
    async def get_members(self, chat_username: str) -> list:
        timeout = 300
        count = self.get_count_members()
        mem = 50
        if count >= mem:
            logger.info(f'В чате больше {mem} участников, начинается подготовка юзербота..\n Зпуск через {timeout // 60} минут') 
            asyncio.sleep(timeout)
            await collect_user_ids(client=multi.get_or_switch_client(False), chat_username=chat_username)
        else:
            logger.info(f'В чате меньше {mem} участников, парс не требуется. {count}')
            return []
    
    async def save_to_db_data(self, chat_username: str):
        try:
            date = date_moscow(option='time_and_date')
            admins = await self.get_chat_admins()
            creator = await self.get_chat_creator()
            inviter_id = await self.get_inviter_id()
            members = await self.get_members(chat_username)
            count_members = await self.get_count_members()

            chat_cache_result = await self.db_session.execute(
                select(ChatCache).where(ChatCache.chat_id == self.chat_id)
            )
            chat_cache = chat_cache_result.scalar_one_or_none()

            if members:
                if count_members == len(members):
                    logger.info(f"✅ Все участники успешно добавлены: count_members == members")
                else:
                    logger.warning(
                        f"⚠️ Некоторые участники не были добавлены!\n"
                        f"count_members: {count_members}, members: {len(members)}"
                    )

                if not chat_cache:
                    chat_cache = ChatCache(
                        chat_id=self.chat_id,
                        members_json={
                            "members": members,
                            "admins": admins
                            },
                        updated_at=date
                    )
                    self.db_session.add(chat_cache)
                else:
                    chat_cache.members_json["members"] = members
                    chat_cache.members_json["admins"] = admins
                    chat_cache.updated_at = date

            bot_chat_result = await self.db_session.execute(
                select(BotChatINFO).where(BotChatINFO.chat_id == self.chat_id)
            )
            bot_chat = bot_chat_result.scalar_one_or_none()

            if not bot_chat:
                bot_chat = BotChatINFO(
                    chat_id=self.chat_id,
                    inviter_id=inviter_id,
                    creator_id=creator,
                    count_members=count_members,
                    joing_bot_at=date
                )
                self.db_session.add(bot_chat)
            else:
                bot_chat.inviter_id = inviter_id
                bot_chat.creator_id = creator
                bot_chat.count_members = count_members
                bot_chat.joing_bot_at = date   

            await self.db_session.commit()
        except Exception as e:
            logger.error(f'Ошибка в классе {__class__.__name__}, в модуле save_to_db_data:\n {e}')
            
            
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
        self.event = event
        self.user_id = user_id
        self.chat_id = chat_id
    
    async def check_spammer(self):
        pass
    
    async def save_data(self):
        role = self.event.new_chat_member.status
        warning_spammer = self.check_spammer()
        __new_user__.cashed(
            'new_user',
            data={
                self.chat_id: {
                    self.user_id: {
                        'chat_id': self.chat_id,
                        'user_id': self.user_id,
                        'warning_spammer': warning_spammer,
                        'role': role,
                        'joing_date': create_date,
                        }
                    }
                },
            )


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
                    exiting = await self.dao.create({user_id})
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