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

        return result.first()
