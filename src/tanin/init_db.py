import asyncio
import sys

from tanin.core.config import settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlmodel import SQLModel
from tanin.models.user_model import User
from tanin.utils import logger
from tanin.utils.logger import Module
from sqlalchemy.ext.asyncio import create_async_engine

logger = logger.get_logger(Module.DB)


async def init_db(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database created successfully.")


async def main():
    logger.info("Creating async engine for DB initialization...")

    async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    try:
        logger.info("Initializing database...")
        await init_db(async_engine)
        logger.info("Database initialization complete.")
    finally:
        logger.info("Closing engine connections...")
        await async_engine.dispose()
        logger.info("Engine connections closed.")


if __name__ == '__main__':
    asyncio.run(main())
