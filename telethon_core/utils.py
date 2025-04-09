import logging

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import PeerChannel
from telethon.errors import UserAlreadyParticipantError
import asyncio


logger = logging.getLogger(__name__)

async def collect_user_ids(client: TelegramClient, chat_username: str) -> list:
    try:
        if chat.startswith("https://t.me/"):
            chat = chat.replace("https://t.me/", "")
        
        try:
            await client(JoinChannelRequest(chat_username))
        except UserAlreadyParticipantError:
            pass
        
        user_ids = []
        async for user in client.get_participants(chat_username):
            user_ids.append(user.id)
            print(f"{user.id} — {user.first_name} (@{user.username})")
        
        logger.info(f'Всего участников: {len(user_ids)}')
        return user_ids
        
    except Exception as e:
        logger.error(f'Ошибка в функции collect_user_ids:\n {e}')
        return []
    
    