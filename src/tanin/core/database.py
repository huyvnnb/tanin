from typing import AsyncGenerator, Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends
from tanin.core.config import settings
from redis.asyncio import Redis, from_url
from tanin.utils import logger
from tanin.utils.logger import Module

logger = logger.get_logger(Module.CONFIG)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False, autocommit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_redis_client() -> Redis:
    redis_client = from_url(settings.REDIS_URL, decode_responses=True)
    logger.info(f"Redis client created for URL: {settings.REDIS_URL}")
    return redis_client
