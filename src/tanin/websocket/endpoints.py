import uuid

from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect

from tanin.core.dependencies import get_matching_service, get_connection_manager
from tanin.core.security import get_current_active_user_ws
from tanin.schemas.chat_schema import ClientEvent, StartSearchingEvent, MatchedEvent, SendTextMessageEvent, ChatMessage, \
    NewTextMessageEvent, LeaveRoomEvent, PartnerLeftEvent, WebRTCOfferEvent, WebRTCAnswerEvent, WebRTCICECandidateEvent, \
    PartnerWebRTCOfferEvent, PartnerWebRTCAnswerEvent, PartnerWebRTCICECandidateEvent, VideoCallInitiateEvent, \
    StartWebRTCNegotiationEvent, PartnerWantsVideoEvent
from tanin.schemas.user_schema import ActiveUser
from tanin.utils.logger import Module
from tanin.websocket.connection_manager import ConnectionManager
import pydantic
from tanin.utils import logger
from tanin.websocket.matching_service import MatchingService

router = APIRouter()

logger = logger.get_logger(Module.WEBSOCKET)


async def handle_user_departure(
        user: ActiveUser,
        manager: ConnectionManager,
        matching_service: MatchingService
):
    logger.info(f"Handling departure for user {user.id}")
    await manager.disconnect(user.id)
    partner_id = await matching_service.leave_room(user.id)
    if partner_id:
        logger.info(f"User {user.id} left room. Notifying partner {partner_id}")
        await manager.broadcast_event_to_user(PartnerLeftEvent(), partner_id)
    await matching_service.remove_from_pool(user.id)


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        user: ActiveUser = Depends(get_current_active_user_ws),
        manager: ConnectionManager = Depends(get_connection_manager),
        matching_service: MatchingService = Depends(get_matching_service)
):
    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_json()
            logger.info(data)
            try:
                event = pydantic.parse_obj_as(ClientEvent, data)
                logger.info(event)
            except pydantic.ValidationError:
                continue

            if isinstance(event, StartSearchingEvent):
                await matching_service.add_to_pool(user)

                match = await matching_service.find_and_create_match()
                if match:
                    user1_id, user2_id, room_id = match
                    user1_info = {"id": user1_id, "display_name": "Stranger"}
                    user2_info = {"id": user2_id, "display_name": "Stranger"}

                    logger.info(user1_info)
                    logger.info(user2_info)

                    await manager.broadcast_event_to_user(MatchedEvent(room_id=room_id, partner=user2_info), user1_id)
                    await manager.broadcast_event_to_user(MatchedEvent(room_id=room_id, partner=user1_info), user2_id)

            elif isinstance(event, SendTextMessageEvent):
                room_info = await matching_service.get_user_room_info(user.id)
                if not room_info:
                    continue

                _, partner_id = room_info
                chat_message = ChatMessage(id=uuid.uuid4(), sender_id=user.id, content=event.content)

                logger.info(room_info)
                logger.info(chat_message)

                await manager.broadcast_event_to_user(NewTextMessageEvent(message=chat_message), partner_id)

            elif isinstance(event, VideoCallInitiateEvent):
                room_info = await matching_service.get_user_room_info(user.id)
                if not room_info:
                    continue

                room_id, partner_id = room_info
                await matching_service.set_user_ready_for_video(room_id, user.id)

                both_ready = await matching_service.check_if_both_ready_for_video(room_id)
                if both_ready:
                    logger.info(f"Both users in room {room_id} are ready for video. Initiating negotiation.")
                    await manager.broadcast_event_to_user(StartWebRTCNegotiationEvent(should_create_offer=True), user.id)
                    await manager.broadcast_event_to_user(StartWebRTCNegotiationEvent(should_create_offer=False), partner_id)

                else:
                    logger.info(f"User {user.id} wants video. Notifying partner {partner_id}.")
                    await manager.broadcast_event_to_user(PartnerWantsVideoEvent(), partner_id)

            elif isinstance(event, WebRTCOfferEvent):
                room_info = await matching_service.get_user_room_info(user.id)
                if not room_info: continue
                _, partner_id = room_info

                await manager.broadcast_event_to_user(
                    PartnerWebRTCOfferEvent(sdp=event.sdp),
                    partner_id
                )

            elif isinstance(event, WebRTCAnswerEvent):
                room_info = await matching_service.get_user_room_info(user.id)
                if not room_info:
                    continue
                _, partner_id = room_info

                await manager.broadcast_event_to_user(
                    PartnerWebRTCAnswerEvent(sdp=event.sdp),
                    partner_id
                )

            elif isinstance(event, WebRTCICECandidateEvent):
                room_info = await matching_service.get_user_room_info(user.id)
                if not room_info:
                    continue
                _, partner_id = room_info

                await manager.broadcast_event_to_user(
                    PartnerWebRTCICECandidateEvent(candidate=event.candidate),
                    partner_id
                )

            elif isinstance(event, LeaveRoomEvent):
                partner_id = await matching_service.leave_room(user.id)
                if partner_id:
                    await manager.broadcast_event_to_user(PartnerLeftEvent(), partner_id)

    except WebSocketDisconnect:
        await manager.disconnect(user.id)
        partner_id = await matching_service.leave_room(user.id)
        if partner_id:
            await manager.broadcast_event_to_user(PartnerLeftEvent(), partner_id)

        await matching_service.remove_from_pool(user.id)

# =================================
# @router.get("/find/{client_id}",
#             status_code=status.HTTP_200_OK,
#             response_model=ModelResponse[Union[ChatFind, Conversation]],
#             response_model_exclude_none=True
#             )
# async def start_connect(client_id: UUID, service: MatchService = Depends(get_match_service)):
#     if redis.scard("users") == 0:
#         redis.sadd("users", str(client_id))
#         return ModelResponse(
#             data=ChatFind(client_id=client_id, status="finding"),
#             message="Please waiting for connection..."
#         )
#     else:
#         stranger = redis.srandmember("users")
#         redis.srem("users", stranger)
#         conversation_id = service.match(client_id, stranger)
#         response = Conversation(
#             conversation_id=conversation_id,
#             peoples=ChatFound(client_id=client_id, stranger=stranger)
#         )
#         return ModelResponse(
#             data=response,
#             message=f"Found client with id {stranger}, starting conversation..."
#         )
#
#
# @router.get("/disconnect/{conversation_id}")
# async def terminate_connect(conversation_id: UUID, service: MatchService = Depends(get_match_service)):
#     service.disconnect(str(conversation_id))
#     return ModelResponse(
#         message="End conversation successfully."
#     )
#
#
# @router.websocket("/ws/{conversation_id}")
# async def websocket_chat(websocket: WebSocket, conversation_id: UUID):
#     await websocket.accept()
#     await manager.connect(websocket, conversation_id)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.send_message(data, websocket)
#     except WebSocketDisconnect:
#         logger.warning(f"{conversation_id} is not exist.")
#         await manager.disconnect(conversation_id)
#     except Exception as e:
#         logger.error(f"Lỗi xảy ra với {conversation_id}: {e}")
#         await manager.disconnect(conversation_id)
