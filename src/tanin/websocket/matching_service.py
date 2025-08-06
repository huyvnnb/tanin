import uuid
from uuid import UUID

from tanin.schemas.chat_schema import Conversation
from tanin.websocket.redis_server import redis


class MatchService:
    def match(self, user_a: UUID, user_b: UUID):
        conversation_id = str(uuid.uuid4())
        redis.sadd(f"chat:{conversation_id}:users", str(user_a), str(user_b))
        redis.set(f"chat:{conversation_id}:status", "active")

        return conversation_id

    def disconnect(self, conversation_id: str):
        redis.delete(f"chat:{conversation_id}:users")
        redis.delete(f"chat:{conversation_id}:status")


def get_match_service():
    return MatchService()
