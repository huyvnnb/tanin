from typing import Dict, List
from uuid import UUID
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}

    async def connect(self, websocket: WebSocket, conversation_id: UUID):
        self.active_connections[conversation_id] = websocket

    async def disconnect(self, conversation_id: UUID):
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, conversation_id: UUID):
        if conversation_id in self.active_connections:
            await self.active_connections[conversation_id].send_text(message)


manager = ConnectionManager()
