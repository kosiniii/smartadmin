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

__user_message__ = RedisBase('user_message', dict)    
__new_user__ = RedisBase('new_user', dict)
__mute_users__ = RedisBase('mute_users', dict)
__ban_users__ = RedisBase('ban_users', dict)