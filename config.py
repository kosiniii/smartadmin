import os
from typing import Any
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def env_import(key: str) -> Any:
    MAIN_BOT_TOKEN = os.getenv('MAIN_BOT_TOKEN')
    LOCALHOST_WEBHOOK = os.getenv('LOCALHOST_WEBHOOK')
    LOCALHOST_WEBHOOK_PORT = int(os.getenv('LOCALHOST_WEBHOOK_PORT'))
    LOCALHOST_WEBHOOK_HOST = os.getenv('LOCALHOST_WEBHOOK_HOST')
    LOCALHOST_DATABASE_URL = os.getenv('LOCALHOST_DATABASE_URL')
    ADMIN_ID = int(os.getenv('ADMIN_ID'))
    MAIN_BOT_USERNAME = os.getenv('MAIN_BOT_USERNAME')
    PROJECT_ON_GITHUB = os.getenv('PROJECT_ON_GITHUB')
    
    stack = {
        'MAIN_BOT_TOKEN': MAIN_BOT_TOKEN,
        'LOCALHOST_WEBHOOK': LOCALHOST_WEBHOOK,
        'LOCALHOST_WEBHOOK_PORT': LOCALHOST_WEBHOOK_PORT,
        'LOCALHOST_WEBHOOK_HOST': LOCALHOST_WEBHOOK_HOST,
        'LOCALHOST_DATABASE_URL': LOCALHOST_DATABASE_URL,
        'ADMIN_ID': ADMIN_ID,
        'MAIN_BOT_USERNAME': "@".join(MAIN_BOT_USERNAME),
        'PROJECT_ON_GITHUB': PROJECT_ON_GITHUB
    }
    
    for keys, value in stack.items():
        if keys == key:
            return value
    raise ValueError('Такого элемента нет.')