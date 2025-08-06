import json
from typing import Union
from uuid import UUID

from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect

from tanin.schemas.chat_schema import ChatFind, ChatFound, Conversation
from tanin.schemas.response_schema import ModelResponse
from tanin.utils.logger import Module
from tanin.websocket.connection_manager import manager
from tanin.websocket.matching_service import MatchService, get_match_service
from tanin.websocket.redis_server import redis
from starlette import status
from tanin.utils import logger

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


logger = logger.get_logger(Module.WEBSOCKET)


@router.get("/find/{client_id}",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[Union[ChatFind, Conversation]],
            response_model_exclude_none=True
            )
async def start_connect(client_id: UUID, service: MatchService = Depends(get_match_service)):
    if redis.scard("users") == 0:
        redis.sadd("users", str(client_id))
        return ModelResponse(
            data=ChatFind(client_id=client_id, status="finding"),
            message="Please waiting for connection..."
        )
    else:
        stranger = redis.srandmember("users")
        redis.srem("users", stranger)
        conversation_id = service.match(client_id, stranger)
        response = Conversation(
            conversation_id=conversation_id,
            peoples=ChatFound(client_id=client_id, stranger=stranger)
        )
        return ModelResponse(
            data=response,
            message=f"Found client with id {stranger}, starting conversation..."
        )


@router.get("/disconnect/{conversation_id}")
async def terminate_connect(conversation_id: UUID, service: MatchService = Depends(get_match_service)):
    service.disconnect(str(conversation_id))
    return ModelResponse(
        message="End conversation successfully."
    )


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: UUID):
    await websocket.accept()
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(data, websocket)
    except WebSocketDisconnect:
        logger.warning(f"{conversation_id} is not exist.")
        await manager.disconnect(conversation_id)
    except Exception as e:
        logger.error(f"Lỗi xảy ra với {conversation_id}: {e}")
        await manager.disconnect(conversation_id)

