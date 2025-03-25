import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT, BigInteger, Date, Float, ForeignKey, func
from sqlalchemy import select, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from utils.inputing import __env__

Base = declarative_base()

engine = create_async_engine(__env__('LOCALHOST_DATABASE_URL'), future=True, echo=False, poolclass=pool.NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    user_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    admin_status = Column(String, nullable=False, default='user')
    

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)