from datetime import datetime, timezone
from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel, UUID4, Field


class ChatMessage(BaseModel):
    id: UUID
    sender_id: UUID
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SendTextMessageEvent(BaseModel):
    event_type: Literal["send_text_message"] = "send_text_message"
    content: str


class StartSearchingEvent(BaseModel):
    event_type: Literal["start_searching"] = "start_searching"


class LeaveRoomEvent(BaseModel):
    event_type: Literal["leave_room"] = "leave_room"


ClientEvent = Union[SendTextMessageEvent, StartSearchingEvent, LeaveRoomEvent]


class MatchedEvent(BaseModel):
    event_type: Literal["matched_event"] = "matched"
    room_id: UUID
    partner: dict


class NewTextMessageEvent(BaseModel):
    event_type: Literal["new_text_message"] = "new_text_message"
    message: ChatMessage


class PartnerLeftEvent(BaseModel):
    event_type: Literal["partner_left"] = "partner_left"


class ErrorEvent(BaseModel):
    event_type: Literal["error"] = "error"
    message: str


ServerEvent = Union[MatchedEvent, NewTextMessageEvent, PartnerLeftEvent, ErrorEvent]

# =================================
# class ChatFind(BaseModel):
#     client_id: UUID
#     status: str
#
#
# class ChatFound(BaseModel):
#     client_id: UUID
#     stranger: UUID
#
#
# class Conversation(BaseModel):
#     conversation_id: str
#     peoples: ChatFound
