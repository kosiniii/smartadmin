import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from commands.states.state import panell, stars_count
from config import env_import
from data.sqltables import MePayments, User
from keyborads.inline import commands_help_admin, dash_panel, pay_stars
from utils.dataclass import BasicUser
from utils.tools import BaseDAO, PaymentService, UpdateDAO, Update_date, changes_data
from utils.inputing import __env__
from utils.inputing import bot

logger = logging.getLogger(__name__)

router = Router(name=__name__)

@router.message(Command(commands='start', prefix='/'))
async def starting(message: Message):
    await message.answer(
        text='🚀 Я бот администратор.\n'
        '/help Посмотреть как использовать\n'
        '/donate Если вы хотите поддержать разработчика\n\n'
        '/settings Настроить бота'
        '/see Посмотреть статистику чата',
        reply_markup=dash_panel()
        )
        
@router.message(Command('/see', prefix='/'))
async def seemore(message: Message, db_session: AsyncSession):
    pass

@router.message(Command('settings', prefix='/'))
async def commsettings():
    pass

@router.message(Command(commands='/donate', prefix='/'))
async def me_donation(message: Message, state: FSMContext):
    await message.answer(
        text='Оу, я вижу что вы хотите поддержать проект 😁,\n'
        '🤩 Введите кол-во звезд,\n'
        'которое хотите пожертвовать проекту:'
        )
    await state.set_state(stars_count.count)  
    
    
@router.message(StateFilter(stars_count.count))
async def create_payment_stars(message: Message, state: FSMContext):
    user = BasicUser.from_message(message)
    stars_dinamic = int(message.text)
    if stars_dinamic <= 0:
        await message.answer('🔔 Кол-во звезд должно быть больше 0. Введите снова.')
        return
    
    await state.update_data({'stars_count': stars_count})
    result_price = stars_dinamic * 200
        
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Покупка звезд",
        description=f"Вы жертвуете {stars_dinamic} звезд!",
        payload=f"purchase_stars_{user.user_id}",
        provider_token=__env__('PROVIDER_TOKEN_PAY'),
        currency="STARS",
        prices=[LabeledPrice(label=f"{stars_dinamic} Звезд", amount=result_price)],
        start_parameter="stars_payment",
        reply_markup=pay_stars(),
    )
    
    await state.clear()
    
    
@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True) 

@router.message(lambda msg: msg.successful_payment and msg.chat.type == "private")
async def successful_payment(message: Message, db_session: AsyncSession):
    user_id = message.from_user.id
    amount = message.successful_payment.total_amount / 200
    amount_rub = amount * 2
    
    paym = PaymentService(db_session)
    data = paym.add_or_update_payment(user_id, amount)
    if data:
        payment_count: int = data.get('payment_count')
  
        logger.info(f'Оплата прошла:\n amount: {amount_rub}\n user_id: {user_id}') 
        result_text = (f'\n Вы донатите уже {markdown.hbold(payment_count)} раза!'
                    f'\n 💫 Звезд сколько вы уже задонатили: {markdown.hbold(amount)} 💫'
                    f'\n Огромное вам спасибо 🤗')          
        await message.answer(
            f"❤️ Огромное спасибо за кровно потраченные {markdown.hbold(amount_rub)}₽ ❤️"
            f"{f'\n {result_text if payment_count > 1 else None}'}"
        )
    else:
        await message.answer('Произошла ошибка при получении данных.')
        logger.info('Ошибка в base.changes_data()')
    

@router.message(Command('help', prefix='/'))
async def help_for_admins(message: Message):
    await message.answer(
        text='Ознакомься с командами и с их настройкой',
        reply_markup=commands_help_admin()
        )

@router.message(Command.commands['/start', '/donate', '/help', '/settings'])  
async def commands_add(message: Message, db_session: AsyncSession):
    user = BasicUser.from_message(message)
    response = User.user_id == user.user_id
    data = {
            'user_id': user.user_id,
            'user_name': user.user_name,
            'full_name': user.full_name,
            'admin_status': admin_status        
        }
    ADMIN_ID = __env__('ADMIN_ID')
    admin_status = 'user'
    
    if isinstance(ADMIN_ID, int) and ' ' not in ADMIN_ID:
        if user.user_id == ADMIN_ID:
            admin_status = 'admin'
    else:
        for ids in ADMIN_ID:
            if ids == user.user_id:
                admin_status = 'admin'
    
    dao = BaseDAO(User, db_session)
    exiting = dao.get_one(response)
    if exiting:
        dao.update(
            base=exiting,
            params={data}
        )
    else:
        dao.create(
            data={data}
        )


