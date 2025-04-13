import os
from typing import Any
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


def env_import(key: str | list) -> Any | list[Any]:
    MAIN_BOT_TOKEN = os.getenv('MAIN_BOT_TOKEN')
    LOCALHOST_WEBHOOK = os.getenv('LOCALHOST_WEBHOOK')
    LOCALHOST_WEBHOOK_PORT = int(os.getenv('LOCALHOST_WEBHOOK_PORT'))
    LOCALHOST_WEBHOOK_HOST = os.getenv('LOCALHOST_WEBHOOK_HOST')
    LOCALHOST_DATABASE_URL = os.getenv('LOCALHOST_DATABASE_URL')
    ADMIN_ID = int(os.getenv('ADMIN_ID'))
    MAIN_BOT_USERNAME = os.getenv('MAIN_BOT_USERNAME')
    PROJECT_ON_GITHUB = os.getenv('PROJECT_ON_GITHUB')
    PROVIDER_TOKEN_PAY = os.getenv('PROVIDER_TOKEN_PAY')
    LOCALHOST_REDIS_HOST = os.getenv('LOCALHOST_REDIS_HOST')
    LOCALHOST_REDIS_PORT = int(os.getenv('LOCALHOST_REDIS_PORT'))
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
    
    stack = {
        'MAIN_BOT_TOKEN': MAIN_BOT_TOKEN,
        'LOCALHOST_WEBHOOK': LOCALHOST_WEBHOOK,
        'LOCALHOST_WEBHOOK_PORT': LOCALHOST_WEBHOOK_PORT,
        'LOCALHOST_WEBHOOK_HOST': LOCALHOST_WEBHOOK_HOST,
        'LOCALHOST_DATABASE_URL': LOCALHOST_DATABASE_URL,
        'ADMIN_ID': ADMIN_ID,
        'MAIN_BOT_USERNAME': "@".join(MAIN_BOT_USERNAME),
        'PROJECT_ON_GITHUB': PROJECT_ON_GITHUB,
        'PROVIDER_TOKEN_PAY': PROVIDER_TOKEN_PAY,
        'LOCALHOST_REDIS_HOST': LOCALHOST_REDIS_HOST,
        'LOCALHOST_REDIS_PORT': LOCALHOST_REDIS_PORT,
        'API_ID': API_ID,
        'API_HASH': API_HASH,
        'PHONE_NUMBER': PHONE_NUMBER
    }
    if isinstance(key, list):
        lkey = len(key)
        if lkey <= 1:
            raise ValueError('Передан один элемент в списке')
        
        result = []
        for item in key:
            for keys, value in stack.items():
                if item == key:
                    result.append(value)
        if result:
            return result
        raise ValueError(f'Эти элементы не были найдены: {key[:lkey - 1]}')
                
    if isinstance(key, str):
        for keys, value in stack.items():
            if keys == key:
                return value
        raise ValueError(f'Такого элемента как {key} нет')
    
__env__ = env_import