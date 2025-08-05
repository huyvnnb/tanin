from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class User(SQLModel, table=True):

    __tablename__ = 'users'

    id: UUID = Field(primary_key=True, nullable=False, index=True, default_factory=uuid4)
    username: EmailStr = Field(unique=True, index=True, max_length=255, nullable=False)
    password_hash: Optional[str] = Field(nullable=False, max_length=255)
    display_name: Optional[str] = Field()
    avatar: Optional[str] = Field()
