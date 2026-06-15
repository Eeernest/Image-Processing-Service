import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

DATABASE_URL = settings.POSTGRES_URL

engine = create_async_engine(
  DATABASE_URL,
  echo=False,
  pool_pre_ping=True,
  pool_size=20,
  max_overflow=30
)

AsyncSessionLocal = async_sessionmaker(
  bind=engine,
  expire_on_commit=False,
  autocommit=False,
  autoflush=False
)

class Base(DeclarativeBase):
  pass

async def get_session():
  async with AsyncSessionLocal() as session:
    yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]