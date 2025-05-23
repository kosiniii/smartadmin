import asyncio
from datetime import datetime, timedelta
from sqlalchemy import DateTime, select, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT, BigInteger, Date, Float, ForeignKey, func
from sqlalchemy import select, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from utils.inputing import __env__
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from utils.tools import date_moscow

Base = declarative_base()
engine = create_async_engine(__env__('LOCALHOST_DATABASE_URL'), future=True, echo=False, poolclass=pool.NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

# Basic information
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    user_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    admin_status = Column(String, nullable=False, default='user')
    
    payments = relationship("MePayments", back_populates="user")
    
class MePayments(Base):
    __tablename__ = "payments"
       
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    donated_stars = Column(BigInteger, nullable=False, default=0)
    payment_count = Column(BigInteger, nullable=False, default=0)

    user = relationship('User', back_populates='payments')



# Chat information    
class BotChatINFO(Base):
    __tablename__ = "chats"

    chat_id = Column(BigInteger, primary_key=True)
    chat_username = Column(String, nullable=True)
    inviter_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    count_members = Column(BigInteger, nullable=False, default=1)
    join_bot_at = Column(String, nullable=False)
    

class SavesSettings(Base):
    __tablename__ = 'saves_settings'
    user_id = Column(BigInteger, ForeignKey('users.user_id'), index=True)
    config_chats = Column(JSONB, nullable=True) # [chat_id or [chat_id, chat_id если конфиг не отличается]: {config}]
    
    
class ChatMember(Base):
    __tablename__ = "chat_members"
    chat_id = Column(BigInteger, ForeignKey("chats.chat_id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String, nullable=False) 
    joined_at = Column(String, nullable=False)
    update_data = Column(String, nullable=False)

    chat = relationship("BotChatINFO", back_populates="members")

class DangersFromTheUser(Base):
    __tablename__ = 'dangers'
    
    user_id = Column(BigInteger, ForeignKey("ChatMember.user_id"), nullable=False)
    count_mute = Column(BigInteger, default=0)
    count_ban = Column(BigInteger, default=0)
    active_mute = Column(BigInteger, default=0)
    active_ban = Column(BigInteger, default=0)
    cache_date_user = Column(JSONB) # {chat_id: {mute: {start_date: str | int, end_date: str | int}, ban: str Типо есть или нет | bool}
    percent_danger = Column(JSONB) # insult: [str | None], scam: [str | None], spam: [str | None], conclusion: str | None}

    user_id = relationship('ChatMember', back_populates='dangers')

class MessageUser(Base):
    __tablename__ = "messages"
    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.chat_id"), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    message_text = Column(String, nullable=False)
    send_date = Column(String, nullable=False)
    
    chat = relationship("BotChatINFO", back_populates="messages")
    
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)