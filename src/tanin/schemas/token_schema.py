from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: Optional[UUID] = None