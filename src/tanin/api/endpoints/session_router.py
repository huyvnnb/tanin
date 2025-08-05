import uuid

from fastapi import APIRouter
from starlette import status

from tanin.schemas.response_schema import ModelResponse
from tanin.schemas.user_schema import AnonymousResponse

router = APIRouter(
    prefix="/session",
    tags=["Session"]
)


@router.get("/anonymous",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[AnonymousResponse],
            response_model_exclude_none=True
            )
async def get_anonymous_identifier():
    response = AnonymousResponse(
        client_id=uuid.uuid4()
    )
    return ModelResponse(
        data=response,
        message="Fetch client id successfully"
    )
