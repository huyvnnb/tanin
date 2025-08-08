from functools import lru_cache

from tanin.core.database import get_redis_client
from redis.asyncio import Redis

from tanin.websocket.connection_manager import ConnectionManager
from tanin.websocket.matching_service import MatchingService


@lru_cache(maxsize=None)
def get_redis() -> Redis:
    return get_redis_client()


@lru_cache(maxsize=None)
def get_connection_manager() -> ConnectionManager:
    return ConnectionManager(get_redis())


@lru_cache(maxsize=None)
def get_matching_service() -> MatchingService:
    return MatchingService(get_redis())
