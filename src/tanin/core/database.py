import asyncio
from typing import AsyncGenerator, Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends, Request
from tanin.core.config import settings
from redis.asyncio import Redis, from_url
from tanin.utils import logger
from tanin.utils.logger import Module

logger = logger.get_logger(Module.CONFIG)


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_redis_client() -> Redis:
    redis_client = from_url(settings.REDIS_URL, decode_responses=True)
    logger.info(f"Redis client created for URL: {settings.REDIS_URL}")
    return redis_client
