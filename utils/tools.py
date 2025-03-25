import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from dataclasses import dataclass
logger = logging.getLogger(__name__)

class Update_date:
    def __init__(self, base, params: dict[str, Any]):
        self.base = base
        self.params = params
    
    def update(self):
        for key, items in self.params.items():
            if hasattr(self.base, key):
                if getattr(self.base, key) != items:
                    setattr(self.base, key, items)
            else:
                logger.error(f"Не найден атрибут '{key}' в объекте {self.base.__class__.__name__}")
    
    async def save_(self, db_session: AsyncSession):
        try:
            self.update()
            db_session.add(self.base)
            await db_session.commit()
        except Exception as e:
            logger.error(f'Ошибка при сохранении в бд: {e}')
            await db_session.rollback()
            
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
