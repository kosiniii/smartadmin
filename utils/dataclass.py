from dataclasses import dataclass
from aiogram.types import Message


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
            chat_id = message.chat.id,
            message_text = message.text,    
        )
   
@dataclass(eq=False)
class TelethonLog:
    api_id: int
    api_hash: str
    phone_number: str

    def return_self(self):
        log = f'| api_id: {self.api_id} |\n| api_hash: {self.api_hash} |\n| phone_number: {self.phone_number} |'
        return log