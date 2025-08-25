from functools import lru_cache

from tanin.core.config import settings
from tanin.core.database import get_redis_client
from redis.asyncio import Redis

from tanin.middlewares.token_bucket import TokenBucketManager
from tanin.utils.logger import Module
from tanin.websocket.connection_manager import ConnectionManager
from tanin.websocket.matching_service import MatchingService
from tanin.utils import logger

logger = logger.get_logger(Module.DEP)


@lru_cache(maxsize=None)
def get_redis() -> Redis:
    return get_redis_client()


@lru_cache(maxsize=None)
def get_connection_manager() -> ConnectionManager:
    return ConnectionManager(get_redis())


@lru_cache(maxsize=None)
def get_matching_service() -> MatchingService:
    return MatchingService(get_redis())


@lru_cache(maxsize=None)
def get_token_bucket_manager() -> TokenBucketManager:
    logger.info("Initialize Token Bucket Manager")
    return TokenBucketManager(get_redis(), capacity=settings.RATE_LIMIT_CAPACITY, refill_rate=settings.RATE_LIMIT_REFILL_RATE)
