from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ActiveUser(BaseModel):
    id: UUID
    display_name: str
    is_anonymous: bool
    avatar: Optional[str] = None


class AnonymousResponse(BaseModel):
    client_id: UUID
