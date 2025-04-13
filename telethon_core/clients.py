import asyncio
import logging
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
from telethon_core.settings import TelegramAPI
from telethon_core.utils import *
from itertools import cycle
from utils.inputing import __env__
from main import ask
logger = logging.getLogger(__name__)

class MultiAccountManager:
    def __init__(self, accounts_data):
        self.accounts_data = accounts_data
        self.clients = {}
        self.client_cycle = None
        self.current_client = None
        # bot
        self.bot_start = False
        self.bot_client = None
        self.is_bot_attached = False

    async def start_clients(self):
        if ask == "no":
            logger.info('Был произведен запуск без telethon')
            return 
        
        if not self.accounts_data or len(self.accounts_data) == 0 or \
        any(not account.get('api_id') or not account.get('api_hash') or not account.get('phone_number') \
            for account in self.accounts_data):
            logger.error('Словари в списке пусты, telethon не запущен!')
            return
        
        i = 0
        for account in self.accounts_data:
            api_id = account.get("api_id")
            api_hash = account.get("api_hash")
            phone_number = account.get("phone_number")
            
            if phone_number in self.clients.keys():
                logger.info(f"Аккаунт {phone_number} уже запущен")
                return self.clients[phone_number]
                     
            client = TelegramClient(f'session_{phone_number}', api_id, api_hash)
            try:
                await client.start(phone_number)
                logger.info(f"Аккаунт {phone_number} подключен")
                
                if not self.is_bot_attached and self.bot_start == True:
                    try:
                        await client.start(__env__('MAIN_BOT_TOKEN'))
                        self.bot_client = client
                        self.is_bot_attached = True
                        logger.info(f"Бот запущен в клиенте {phone_number}")
                    except Exception as e:
                        logger.error(f"Ошибка при запуске бота: {e}")
                
                self.clients[phone_number] = client
                i += 1
                logger.info(f'Запущен новый клиент: {i}!')

            except FloodWaitError as e:
                logger.warning(f"Слишком много запросов.. Ждём {e.seconds} секунд..")
                await asyncio.sleep(e.seconds)
                await client.start(phone_number)
            except Exception as e:
                logger.error(f"Ошибка при подключении: {e}")
                continue
                
        logger.info(f'Кол-во запущенных клиентов: {len(self.clients.keys())}')
        if self.clients:
            self.cycle_clients()
        return self.clients


    async def get_or_switch_client(self, next: bool = False):
        if not self.clients:
            await self.start_clients()

        if not self.client_cycle:
            self.client_cycle = cycle(self.clients.values())

        if next or self.current_client is None:
            self.current_client = next(self.client_cycle)
        return self.current_client
    
    def get_bot_client(self):
        if self.is_bot_attached or self.bot_client:
            return self.bot_client
        
        logger.info("Бот не подключен с telethon!")
        return next(iter(self.clients.values()), None)
        
    async def stop_clients(self):
        count = 0
        for phone_number, client in self.clients.items():
            try:
                await client.disconnect()
                logger.info(f"Отключен клиент {phone_number}")
                count += 1
            except Exception as e:
                logger.error(f"Ошибка при отключении клиента {phone_number}: {e}")
        logger.info(f'Все клиенты были отключены: {count} всего')
        
    def cycle_clients(self):
        try:
            self.client_cycle = cycle(self.clients.values())
            return self.client_cycle
        except Exception as e:
            logger.error('Не перепрал в функции cycle_clients: \n {e}')
            
data_telethon = TelegramAPI().create_json()
multi = MultiAccountManager(data_telethon)