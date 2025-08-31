from tanin.core.exceptions import UserExistException, UserNotFoundException, UnauthorizedException
from tanin.core.security import get_password_hash, verify_password
from tanin.models.user_model import User
from tanin.repository.user_repo import UserRepository
from tanin.schemas.user_schema import UserRegister, UserLogin, UserResponse, LoginResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from tanin.utils import logger
from tanin.utils.helper import create_jwt_token
from tanin.utils.logger import Module

logger = logger.get_logger(Module.AUTH_SERVICE)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def register(self, user: UserRegister):
        exist_user = await self.user_repo.get_user_by_username(user.username)
        if exist_user:
            raise UserExistException()

        password_hash = await get_password_hash(user.password)
        save_user = User(
            username=user.username,
            password_hash=password_hash,
            display_name=user.display_name,
            avatar=user.avatar
        )
        user = await self.user_repo.create_user(save_user)
        return UserResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar=user.avatar
        )

    async def login(self, user: UserLogin):
        exist_user = await self.user_repo.get_user_by_username(user.username)
        if not exist_user:
            logger.info(f"Not found user with name: {user.username}")
            raise UserNotFoundException()

        verified = await verify_password(user.password, exist_user.password_hash)
        if not verified:
            raise UnauthorizedException()

        token_payload = {"sub": str(exist_user.id), "username": exist_user.username}
        access_token = create_jwt_token(data=token_payload)
        return LoginResponse(access_token=access_token)