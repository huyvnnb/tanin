from datetime import datetime, timezone
from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field


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


# WebRTC
class WebRTCOfferEvent(BaseModel):
    event_type: Literal["webrtc_offer"] = "webrtc_offer"
    sdp: dict


class WebRTCAnswerEvent(BaseModel):
    event_type: Literal["webrtc_answer"] = "webrtc_answer"
    sdp: dict


class WebRTCICECandidateEvent(BaseModel):
    event_type: Literal["webrtc_ice_candidate"] = "webrtc_ice_candidate"
    candidate: dict


class VideoCallInitiateEvent(BaseModel):
    event_type: Literal["video_call_initiate"] = "video_call_initiate"


ClientEvent = Union[
    SendTextMessageEvent, StartSearchingEvent, LeaveRoomEvent,
    WebRTCOfferEvent, WebRTCAnswerEvent, WebRTCICECandidateEvent,
    VideoCallInitiateEvent
]


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


class PartnerWebRTCOfferEvent(BaseModel):
    event_type: Literal["partner_webrtc_offer"] = "partner_webrtc_offer"
    sdp: dict


class PartnerWebRTCAnswerEvent(BaseModel):
    event_type: Literal["partner_webrtc_answer"] = "partner_webrtc_answer"
    sdp: dict


class PartnerWebRTCICECandidateEvent(BaseModel):
    event_type: Literal["partner_webrtc_ice_candidate"] = "partner_webrtc_ice_candidate"
    candidate: dict


class PartnerWantsVideoEvent(BaseModel):
    event_type: Literal["partner_wants_video"] = "partner_wants_video"


class StartWebRTCNegotiationEvent(BaseModel):
    event_type: Literal["start_webrtc_negotiation"] = "start_webrtc_negotiation"
    # Server decides who will create OFFER
    should_create_offer: bool


ServerEvent = Union[
    MatchedEvent,
    NewTextMessageEvent,
    PartnerLeftEvent,
    ErrorEvent,
    PartnerWebRTCOfferEvent,
    PartnerWebRTCAnswerEvent,
    PartnerWebRTCICECandidateEvent,
    PartnerWantsVideoEvent,
    StartWebRTCNegotiationEvent
]

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
