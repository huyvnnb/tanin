import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlmodel import SQLModel
from tanin.core.database import async_engine
from tanin.models.user_model import User
from tanin.utils import logger
from tanin.utils.logger import Module

logger = logger.get_logger(Module.DB)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("✅ Database created successfully.")


async def main():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialization complete.")


if __name__ == '__main__':
    asyncio.run(main())