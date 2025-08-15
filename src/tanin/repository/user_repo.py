from typing import Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from tanin.models.user_model import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, id: UUID) -> Optional[User]:
        statement = select(User).where(User.id == id)
        result = await self.session.exec(statement)

        return result.one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        result = await self.session.exec(statement)

        return result.one_or_none()

    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

