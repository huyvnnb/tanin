import uuid
from typing import Tuple, Optional
from uuid import UUID

from tanin.schemas.user_schema import ActiveUser
from redis.asyncio import Redis


class MatchingService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.WAITING_POOL_KEY = "tanin:waiting_pool"
        self.USER_ROOM_KEY_PREFIX = "tanin:user_room:"
        self.ROOM_INFO_KEY_PREFIX = "tanin:room:"

    async def add_to_pool(self, user: ActiveUser) -> None:
        await self.redis.sadd(self.WAITING_POOL_KEY, str(user.id))

    async def remove_from_pool(self, user_id: UUID) -> None:
        await self.redis.srem(self.WAITING_POOL_KEY, str(user_id))

    async def find_and_create_match(self) -> Optional[Tuple[UUID, UUID, UUID]]:
        if await self.redis.scard(self.WAITING_POOL_KEY) < 2:
            return None

        user1_id_bytes, user2_id_bytes = await self.redis.spop(self.WAITING_POOL_KEY, 2)

        user1_id = str(user1_id_bytes.decode())
        user2_id = str(user2_id_bytes.decode())
        # user1_id, user2_id = await self.redis.spop(self.WAITING_POOL_KEY, 2)
        room_id = str(uuid.uuid4())
        room_key = f"{self.ROOM_INFO_KEY_PREFIX}{room_id}"

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(room_key, mapping={"user1": user1_id, "user2": user2_id})
            pipe.set(f"{self.USER_ROOM_KEY_PREFIX}{user1_id}", room_id)
            pipe.set(f"{self.USER_ROOM_KEY_PREFIX}{user2_id}", room_id)
            await pipe.execute()

        return UUID(user1_id), UUID(user2_id), UUID(room_id)

    async def get_user_room_info(self, user_id: UUID) -> Optional[Tuple[UUID, UUID]]:
        room_id_str = await self.redis.get(f"{self.USER_ROOM_KEY_PREFIX}{str(user_id)}")

        if not room_id_str:
            return None

        room_id = UUID(room_id_str.decode())
        room_key = f"{self.ROOM_INFO_KEY_PREFIX}{room_id}"

        user1_id, user2_id = await self.redis.hmget(room_key, ["user1", "user2"])
        user1_id, user2_id = user1_id.decode(), user2_id.decode()

        partner_id = user1_id if user_id == user2_id else user2_id
        return room_id, UUID(partner_id)

    async def leave_room(self, user_id: UUID) -> Optional[UUID]:
        room_info = await self.get_user_room_info(user_id)

        if not room_info:
            return None

        room_id, partner_id = room_info

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.delete(f"{self.ROOM_INFO_KEY_PREFIX}{room_id}")
            pipe.delete(f"{self.USER_ROOM_KEY_PREFIX}{user_id}")
            pipe.delete(f"{self.USER_ROOM_KEY_PREFIX}{partner_id}")
            await pipe.execute()

        return partner_id

# class MatchService:
#     def match(self, user_a: UUID, user_b: UUID):
#         conversation_id = str(uuid.uuid4())
#         redis.sadd(f"chat:{conversation_id}:users", str(user_a), str(user_b))
#         redis.set(f"chat:{conversation_id}:status", "active")
#
#         return conversation_id
#
#     def disconnect(self, conversation_id: str):
#         redis.delete(f"chat:{conversation_id}:users")
#         redis.delete(f"chat:{conversation_id}:status")
#
#
# def get_match_service():
#     return MatchService()
