from fastapi import APIRouter

from tanin.core.database import AsyncSessionDep
from tanin.core.security import get_current_active_user
from tanin.schemas.response_schema import ModelResponse
from tanin.schemas.user_schema import ActiveUser, UserResponse
from fastapi import Depends
from starlette import status
from tanin.services.user_service import UserService

router = APIRouter(
    prefix="/me",
    tags=["User"]
)


@router.get("/info",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[UserResponse],
            response_model_exclude_none=True
            )
async def get_me(session: AsyncSessionDep, user: ActiveUser = Depends(get_current_active_user)):
    user_service = UserService(session)

    response = await user_service.get_me(user)
    return ModelResponse(
        data=response,
        message="Fetch user information successfully."
    )