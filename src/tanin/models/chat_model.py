from datetime import datetime, timezone
import enum
from typing import Dict, Any, List, Optional
from uuid import UUID

from sqlmodel import SQLModel, Field, Column, Relationship, PrimaryKeyConstraint, Enum
from sqlalchemy.dialects.postgresql import JSONB


class ChatType(str, enum.Enum):
    direct = "direct"
    group = "group"


class Conversations(SQLModel, table=True):
    __tablename__ = 'conversations'

    id: UUID = Field(primary_key=True)
    type: ChatType = Field(
        default=ChatType.direct,
        sa_column=Column(
            Enum(ChatType, name="chat_type_enum"),
            nullable=False,
            server_default=ChatType.direct.value
        )
    )
    matched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    participants: List["Participants"] = Relationship(back_populates="conversation")
    messages: List["Messages"] = Relationship(back_populates="conversation")


class Participants(SQLModel, table=True):
    __tablename__ = 'participants'

    user_id: UUID = Field(nullable=False, foreign_key="users.id")
    conversation_id: UUID = Field(nullable=False, foreign_key="conversations.id")
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    conversation: Conversations = Relationship(back_populates="participants")

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "conversation_id", name="pk_participants"),
    )


class Messages(SQLModel, table=True):
    __tablename__ = 'message'

    id: Optional[int] = Field(primary_key=True, default=None)
    conversation_id: UUID = Field(nullable=False, foreign_key="conversations.id")
    data: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))

    conversation: Conversations = Relationship(back_populates="messages")
