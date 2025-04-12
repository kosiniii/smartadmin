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
    inviter_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    creator_id = Column(BigInteger, nullable=True)
    count_members = Column(BigInteger, nullable=False, default=1)
    joing_bot_at = Column(String, nullable=False)
    
class ChatMember(Base):
    __tablename__ = 'chat_members'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), index=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), index=True)
    warning_spammer = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'member', 'creator'
    joined_at = Column(String, nullable=False)
    
class ChatCache(Base):
    __tablename__ = "chat_cache"
    chat_id = Column(BigInteger, ForeignKey("chats.chat_id"), primary_key=True)
    members_json = Column(JSONB)  # {"admins": [1, 2], "members": [3, 4, 5]}
    updated_at = Column(String, nullable=False)

class SavesSettings(Base):
    __tablename__ = 'saves_settings'
    chat_id = Column(BigInteger, ForeignKey("chats.chat_id"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), index=True)
    
    
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)