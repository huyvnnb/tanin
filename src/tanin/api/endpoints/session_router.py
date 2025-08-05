import uuid
from uuid import UUID

from fastapi import APIRouter

from tanin.schemas.user_schema import AnonymousResponse

router = APIRouter(
    prefix="/session",
    tags=["Session"]
)


@router.get("/anonymous")
async def get_anonymous_identifier():
    return AnonymousResponse(
        client_id=uuid.uuid4()
    )