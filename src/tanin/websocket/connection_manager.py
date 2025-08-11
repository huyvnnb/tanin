import json
from typing import Dict
from uuid import UUID

from redis.asyncio import Redis
from fastapi import WebSocket

from tanin.schemas.chat_schema import ServerEvent


class ConnectionManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.active_connections: Dict[UUID, WebSocket] = {}
        self.pubsub_channel = "tanin:chat_messages"

    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_event(self, event: ServerEvent, user_id: UUID):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(event.model_dump())

    async def broadcast_event_to_user(self, event: ServerEvent, user_id: UUID):
        message = {
            'recipient_id': str(user_id),
            'event_data': event.model_dump_json()
        }
        await self.redis.publish(self.pubsub_channel, json.dumps(message))

    async def pubsub_listener(self):
        async with self.redis.pubsub() as pubsub:
            await pubsub.subscribe(self.pubsub_channel)
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    recipient_id = UUID(data["recipient_id"])
                    event_data = json.loads(data["event_data"])

                    if recipient_id in self.active_connections:
                        websocket = self.active_connections[recipient_id]
                        await websocket.send_json(event_data)


# class SimpleConnectionManager:
#     def __init__(self):
#         self.active_connections: dict[str, WebSocket] = {}
#
#     async def connect(self, websocket: WebSocket, user_id: str):
#         await websocket.accept()
#         self.active_connections[user_id] = websocket
#         logger.info(f"Người dùng {user_id} đã kết nối. Hiện có {len(self.active_connections)} kết nối.")
#
#     def disconnect(self, user_id: str):
#         if user_id in self.active_connections:
#             del self.active_connections[user_id]
#             logger.info(f"Người dùng {user_id} đã ngắt kết nối.")
#
#     async def send_personal_message(self, message: str, user_id: str):
#         if user_id in self.active_connections:
#             websocket = self.active_connections[user_id]
#             await websocket.send_text(message)
#
#     async def broadcast(self, message: str):
#         for user_id, websocket in self.active_connections.items():
#             await websocket.send_text(message)


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[UUID, WebSocket] = {}
#
#     async def connect(self, websocket: WebSocket, conversation_id: UUID):
#         self.active_connections[conversation_id] = websocket
#
#     async def disconnect(self, conversation_id: UUID):
#         if conversation_id in self.active_connections:
#             del self.active_connections[conversation_id]
#
#     async def send_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)
#
#     async def broadcast(self, message: str, conversation_id: UUID):
#         if conversation_id in self.active_connections:
#             await self.active_connections[conversation_id].send_text(message)


# manager = ConnectionManager()
