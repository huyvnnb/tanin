import uuid

from fastapi import APIRouter
from starlette import status

from tanin.schemas.response_schema import ModelResponse
from tanin.schemas.user_schema import AnonymousResponse

router = APIRouter(
    prefix="/sessions",
    tags=["Session"]
)


@router.post("/anonymous", status_code=status.HTTP_200_OK)
async def get_anonymous_identifier():
    return AnonymousResponse(
        client_id=uuid.uuid4()
    )
    # return ModelResponse(
    #     data=response,
    #     message="Fetch client id successfully"
    # )
