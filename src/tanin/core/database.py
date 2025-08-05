from typing import AsyncGenerator, Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends
from tanin.core.config import settings


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False, autocommit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]
