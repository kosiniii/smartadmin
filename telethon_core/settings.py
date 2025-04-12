import logging
from utils.dataclass import TelethonLog
from utils.inputing import __env__

logger = logging.getLogger(__name__)


API_ID = __env__('API_ID')
API_HASH = __env__('API_HASH')
PHONE_NUMBER = __env__('PHONE_NUMBER')
        
class TelegramAPI:
    def __init__(self):
        self.api_id = API_ID
        self.api_hash = API_HASH
        self.phone_number = API_HASH
    
    def create_json(self) -> list:     
        if not (self.api_id and self.api_hash and self.phone_number):
            logger.error("Переменные окружения не найдены или пустые!")
            return []
        
        api_ids = self.api_id.split(',') if ',' in self.api_id else [self.api_id]
        api_hashes = self.api_hash.split(',') if ',' in self.api_hash else [self.api_hash]
        phone_numbers = self.phone_number.split(',') if ',' in self.phone_number else [self.phone_number]
    
        if not (len(api_ids) == len(api_hashes) == len(phone_numbers)):
            logger.error("Количество API ID, API Hash и номеров телефонов не совпадает!")
            return [] 
        
        accounts = []
        for i in range(len(api_ids)):
            i -= 1
            try:
                account = {
                    "api_id": int(api_ids[i].strip()),
                    "api_hash": api_hashes[i].strip(),
                    "phone_number": phone_numbers[i].strip(),
                }
                accounts.append(account)
            except ValueError:
                logger.error(f"Ошибка в данных аккаунта {i + 1}. Проверь api_id (должно быть число).")

        Log = TelethonLog(self.api_id, self.api_hash, self.phone_number)
        print(Log.return_self())
        return accounts