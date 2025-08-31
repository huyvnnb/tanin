from fastapi import APIRouter

from tanin.core.database import AsyncSessionDep
from tanin.schemas.response_schema import ModelResponse
from tanin.schemas.user_schema import UserRegister, UserResponse, UserLogin, LoginResponse
from tanin.services.auth_service import AuthService
from fastapi import status
from tanin.utils import logger
from tanin.utils.logger import Module

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

logger = logger.get_logger(Module.AUTH_ROUTER)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelResponse[UserResponse],
    response_model_exclude_none=True
)
async def register(user: UserRegister, session: AsyncSessionDep):
    service = AuthService(session)
    response = await service.register(user)

    return ModelResponse(
        data=response,
        message="Create account successfully."
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ModelResponse[LoginResponse],
    response_model_exclude_none=True,
)
async def login(user: UserLogin, session: AsyncSessionDep):
    service = AuthService(session)
    response = await service.login(user)

    return ModelResponse(
        data=response,
        message="Login successfully."
    )
