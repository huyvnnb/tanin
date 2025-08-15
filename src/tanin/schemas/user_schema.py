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


class UserRegister(BaseModel):
    username: str
    password: str
    display_name: str
    avatar: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    display_name: str
    avatar: str
    