from typing import Optional

from tanin.repository.user_repo import UserRepository
from tanin.schemas.user_schema import ActiveUser, UserResponse
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def get_me(self, user: ActiveUser) -> Optional[UserResponse]:
        exist_user = await self.user_repo.get_user_by_id(user.id)
        if not exist_user:
            return None

        return UserResponse(
            id=exist_user.id,
            username=exist_user.username,
            display_name=exist_user.display_name,
            avatar=exist_user.avatar
        )

