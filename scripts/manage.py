import asyncio
import sys
from typing import Annotated

from tanin.core.config import settings
from tanin.core.security import get_password_hash

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import typer
from sqlmodel import SQLModel
from tanin.models.user_model import User
from tanin.models.chat_model import Conversations, Participants, Messages
from tanin.utils import logger
from tanin.utils.logger import Module
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

logger = logger.get_logger(Module.DB)

database = typer.Typer(
    name="database",
    help="Manage database operations like initialization and seeding."
)


async def _create_table(async_engine):
    typer.echo("Connecting to the database to create tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database created successfully.")
    typer.secho("Tables created successfully.", fg=typer.colors.GREEN)


async def _seed_data(async_engine):
    typer.echo("Seeding initial data...")

    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(User).where(User.username == "admin"))
        admin = result.first()

        if not admin:
            hashed_password = await get_password_hash("supersecretpassword")
            new_admin = User(
                username="admin",
                password_hash=hashed_password,
                display_name="Admin",
            )
            session.add(new_admin)
            await session.commit()
            typer.secho("Admin user created.", fg=typer.colors.CYAN)
        else:
            typer.secho("Admin user already exists. Skipping.", fg=typer.colors.YELLOW)

    typer.secho("Data seeding complete.", fg=typer.colors.GREEN)


async def _run_init():
    logger.info("Creating async engine for DB initialization...")

    async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    try:
        logger.info("Initializing database...")
        await _create_table(async_engine)
        logger.info("Database initialization complete.")
    finally:
        logger.info("Closing engine connections...")
        await async_engine.dispose()
        logger.info("Engine connections closed.")


@database.command("create-tables", help="Creates all database tables based on SQLModel metadata.")
def create_tables():
    async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    async def run_create():
        await _create_table(async_engine)
        await async_engine.dispose()

    asyncio.run(run_create())


@database.command("seed-data", help="Seeds the database with initial data (e.g., an admin user).")
def seed_data():
    async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    async def run_seed():
        await _seed_data(async_engine)
        await async_engine.dispose()

    asyncio.run(run_seed())


@database.command("init", help="Initializes the database: Creates tables and seeds initial data.")
def init_db(
    recreate: Annotated[bool, typer.Option("--recreate", "-r", help="Drop all tables before creating.")] = False
):
    async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    async def run_init():
        if recreate:
            confirm = typer.confirm("This action will drop your database. Should use create-tables instead. "
                                    "Do you want to continue?")
            if not confirm:
                typer.echo("Hủy thao tác xoá database.")
                return

            typer.echo("Dropping all tables...")
            async with async_engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.drop_all)
            typer.secho("All tables dropped.", fg=typer.colors.RED)
        await _create_table(async_engine)
        await _seed_data(async_engine)
        await async_engine.dispose()

    asyncio.run(run_init())
