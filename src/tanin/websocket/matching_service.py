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

        user1_id, user2_id = await self.redis.spop(self.WAITING_POOL_KEY, 2)
        if not user1_id or not user2_id:
            return None

        room_id = str(uuid.uuid4())
        room_key = f"{self.ROOM_INFO_KEY_PREFIX}{room_id}"

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(room_key, mapping={"user1": user1_id, "user2": user2_id})
            pipe.set(f"{self.USER_ROOM_KEY_PREFIX}{user1_id}", room_id)
            pipe.set(f"{self.USER_ROOM_KEY_PREFIX}{user2_id}", room_id)
            await pipe.execute()

        return UUID(user1_id), UUID(user2_id), UUID(room_id)

    async def get_user_room_info(self, user_id: UUID) -> Optional[Tuple[UUID, UUID]]:
        room_id = await self.redis.get(f"{self.USER_ROOM_KEY_PREFIX}{str(user_id)}")

        if not room_id:
            return None

        room_id = UUID(room_id)
        room_key = f"{self.ROOM_INFO_KEY_PREFIX}{room_id}"

        user1_id, user2_id = await self.redis.hmget(room_key, ["user1", "user2"])
        if not user1_id or not user2_id:
            return None

        partner_id = user2_id if str(user_id) == user1_id else user1_id
        return room_id, UUID(partner_id)

    async def set_user_ready_for_video(self, room_id: UUID, user_id: UUID):
        room_key = f"{self.ROOM_INFO_KEY_PREFIX}{room_id}"
        room_data = await self.redis.hgetall(room_key)

        if not room_data:
            return

        user_field = "user1_ready_video" if room_data.get("user1") == str(user_id) else "user2_ready_video"
        await self.redis.hset(room_key, user_field, "1")

    async def check_if_both_ready_for_video(self, room_id: UUID) -> bool:
        room_key = f"{self.ROOM_INFO_KEY_PREFIX}{room_id}"
        ready_states = await self.redis.hmget(room_key, ["user1_ready_video", "user2_ready_video"])

        return all(state == "1" for state in ready_states if state is not None)

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
