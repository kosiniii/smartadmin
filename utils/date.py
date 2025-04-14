import logging
import time
from datetime import datetime, timedelta
from typing import Any
from aiogram.utils import markdown
import pytz

logger = logging.getLogger(__name__)
moscow_time = pytz.timezone('Europe/Moscow')

class DateMoscow:
    def __init__(self, option: str):
        self.option = option
        self.now = datetime.now(moscow_time)
    
    def conclusion_date(self) -> str | int:
        if self.option == 'date':
            timed = self.now.date()
        
        elif self.option == 'time_info_style_str':
            timed = self.now.strftime(
                f"Дата: {markdown.hbold(f'%d.%m.%Y')}\n"
                f"Время: {markdown.hbold('%H:%M')}"
                )
        elif self.option == 'time_and_date_str':
            timed = self.now.strftime(f'%d.%m.%Y %H:%M')
        
        elif self.option == 'time_now':
            timed = self.now
            
        elif self.option == 'fromtimestamp':
            timed = int(self.now.timestamp()) # хз шо это 
    
        else:
            raise ValueError('Такого объекта не представленно в функции.')
        return timed
    
    def custom_date(self, add_time: dict | None):   
        new_time = self.now
        
        if add_time:
            years = add_time.get('year', 0)
            months = add_time.get('moth', 0)
            days = add_time.get('day', 0)
            hours = add_time.get('hour', 0)
            minutes = add_time.get('minute', 0)
            seconds = add_time.get('second', 0)
            new_time = self.now + timedelta(
                year = years,
                month = months,
                days = days,
                hours = hours,
                minutes = minutes,
                seconds = seconds
            )
            
        timed = {
            "year": new_time.year,
            "month": new_time.month,
            "day": new_time.day,
            "hour": new_time.hour,
            "minute": new_time.minute,
            "second": new_time.second,
        }

        return timed