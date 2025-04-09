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
from utils.tools import Update_date
from utils.inputing import __env__
from utils.inputing import bot

logger = logging.getLogger(__name__)

router = Router(name=__name__)

@router.message(Command(commands='start', prefix='/'))
async def starting(message: Message):
    await message.answer(
        text='🚀 Я бот администратор.\n'
        'Посмотреть как использовать /help\n'
        'Если вы хотите поддержать разработчика то /donate\n\n'
        'У вас есть вопросы? Вы нашли ошибку? или у вас есть доп. идеи?\n'
        'То обратится в поддержку бота можно на прямую @KociHH\n',
        reply_markup=dash_panel()
        )
  

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

#user_id
#donated_stars
#payment_count

@router.message(lambda msg: msg.successful_payment and msg.chat.type == "private")
async def successful_payment(message: Message, db_session: AsyncSession):
    amount = message.successful_payment.total_amount / 200
    amount_rub = amount * 2
    user_id = message.from_user.id
    base = await db_session.execute(select(MePayments).where(MePayments.user_id == user_id and User.user_id == user_id))
    find_user = base.scalars().one_or_none()
    payment_count = 1 + find_user.payment_count
    stars_amount = amount + find_user.donated_stars
    
    if find_user:
        update = Update_date(
            base=find_user,
            params={
                'user_id': user_id,
                'donated_stars': stars_amount,
                'payment_count': payment_count
            }
        )
        await update.save_(db_session)
    else:
        user = MePayments(
            user_id = user_id,
            donated_stars = amount,
            payment_count = 1
        )
        await db_session.add(user)
        db_session.commit()
    
    logger.info(f'Оплата прошла:\n amount: {amount_rub}\n user_id: {user_id}') 
    result_text = (f'\n Вы донатите уже {markdown.hbold(payment_count)} раза!'
                  f'\n 💫 Звезд сколько вы уже задонатили: {markdown.hbold(amount)} 💫'
                  f'\n Огромное вам спасибо 🤗')          
    await message.answer(
        f"❤️ Огромное спасибо за кровно потраченные {markdown.hbold(amount_rub)}₽ ❤️"
        f"{f'\n {result_text if find_user.payment_count > 1 else None}'}"
        )
    

@router.message(Command('help', prefix='/'))
async def help_for_admins(message: Message):
    await message.answer(
        text='Ознакомься с командами и с их настройкой',
        reply_markup=commands_help_admin()
        )


@router.message(Command.commands['/start', '/donate', '/help'])  
async def commands_add(message: Message, db_session: AsyncSession):
    user = BasicUser.from_message(message)
    
    ADMIN_ID = env_import('ADMIN_ID')
    full_name = user.full_name
    user_id = user.user_id
    user_name = user.user_name
    admin_status = 'user'
    
    if isinstance(ADMIN_ID, int) and ' ' not in ADMIN_ID:
        if user_id == env_import('ADMIN_ID'):
            admin_status = 'admin'
    else:
        for ids in ADMIN_ID:
            if ids == user_id:
                admin_status = 'admin'
    
    base = await db_session.execute(select(User).where(User.user_id == user_id))
    result_base = base.scalars().one_or_none()
    if result_base:
        update = Update_date(
            base=result_base,
            params={
                'user_id': user_id,
                'user_name': user_name,
                'full_name': full_name,
                'admin_status': admin_status
            }
        )
        await update.save_(db_session)
    else:
        user = User(
            user_id = user_id,
            user_name = user_name,
            full_name = full_name,
            admin_status = admin_status
        )
        await db_session.add(user)
        db_session.commit()
        logger.info(f'Пользователь добавлен в бд\n id: {user_id}')


