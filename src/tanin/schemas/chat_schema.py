from uuid import UUID

from pydantic import BaseModel


class ChatFind(BaseModel):
    client_id: UUID
    status: str


class ChatFound(BaseModel):
    client_id: UUID
    stranger: UUID


class Conversation(BaseModel):
    conversation_id: str
    peoples: ChatFound