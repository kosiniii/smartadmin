import json
import logging
from typing import Union
from redis import Redis

redis_client = Redis(host="localhost", port=6379, db=0)
logger = logging.getLogger(__name__)

class RedisBase:
    def __init__(self, key: str, data: Union[dict, list]):
        self.key = key
        self.data = data
    
    def cashed(self, key: str, data: Union[dict, list], ex: int = None) -> None:   
        if isinstance(data, dict):
            data = json.dumps(data)
        try:
            redis_client.set(name=key, value=data, ex=ex)
        except Exception as e:
            logger.error(f'Ошибка в redis: {e}')  
    
    def dict_list(self, param: Union[dict, list]):
        if isinstance(param, dict):
            return {}
        return []
    
    def get_cashed(self, data: Union[dict, list] | None = None, key: str | None = None) -> dict | list:
        if not data:
            data = self.data
        
        if key is None :
            key = self.key 
        
        result = self.dict_list(data)
        try:
            getr = redis_client.get(key)
            if getr:
                try:
                    if isinstance(data, dict):
                        return json.loads(getr)
                    else:
                        return getr
                    
                except json.JSONDecodeError:
                    getr = type(data)
                    return result
            else:
                logger.error(f'Не найден данный ключ: {key}')
                return result
        except Exception as e:
            logger.error(f'Ошибка получения данных: {e}')
            return result    

    def delete_key_fast(self, key: str | None = None) -> None:
        if key is None:
            key = self.key 
            redis_client.delete(key)
        return

__user_warns__ = RedisBase('user_warns', dict) # {user_id: {warn_chats: {count_mute: int, count_ban: int, warnings: {insult: [str | None], scam: [str | None], spam: [str | None], conclusion: str | None}}} в зависимости от __mute_users__, __ban_users__ .get('cause')
__user_last_message__ = RedisBase('user_last_message', dict) # {user_id: {message_id: int, message_text: str, send_date: str | int, chat_id: int}} возможность брать новые user_id .get("user_id")
__new_user__ = RedisBase('new_user', dict) # {chat_id: {user_id: {join_date: str | int, unknown_user: bool}}
__mute_users__ = RedisBase('mute_users', dict) # {user_id: {mute_start: str | int, mute_end: str | int, chat_id: int, cause: str}}
__ban_users__ = RedisBase('ban_users', dict) # {user_id: {ban_start: str | int, ban_end: str | int, chat_id: int, cause: str}}