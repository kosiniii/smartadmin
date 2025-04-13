from datetime import datetime
from aiogram.utils import markdown
import pytz


def date_moscow(option: str) -> int | str:
    moscow_time = pytz.timezone('Europe/Moscow')
    if option == 'date':
        time = datetime.now(moscow_time).date()
    elif option == 'time_info_style':
        time = datetime.now(moscow_time).strftime(
            f"Дата: {markdown.hbold(f'%d.%m.%Y')}\n"
            f"Время: {markdown.hbold('%H:%M')}"
            )
    elif option == 'time_and_date':
        time = datetime.now(moscow_time).strftime(f'%d.%m.%Y %H:%M')
    elif option == 'time_now':
        time = datetime.now(moscow_time)
    else:
        raise ValueError('Такого объекта не представленно в функции.')
    return time