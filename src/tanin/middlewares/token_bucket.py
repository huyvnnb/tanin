import time
from uuid import UUID
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from redis.asyncio import Redis
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from tanin.utils import helper
from tanin.utils import logger
from tanin.utils.logger import Module

log = logger.get_logger(Module.MID)


# In-memory manager
# class TokenBucket:
#     def __init__(self, user_id: str, ip: str, capacity: int = 10, refill_rate: float = 1.0):
#         self.capacity = capacity
#         self.tokens = capacity
#         self.refill_rate = refill_rate
#         self.last_refill = time.time()
#         self.key = f"rate_limit:user:{user_id}" if user_id else f"rate_limit:ip:{ip}"
#
#     def consume(self, amount: int = 1):
#         now = time.time()
#         elapsed = now - self.last_refill
#
#         self.tokens = min(self.capacity, int(self.tokens + self.refill_rate * elapsed))
#
#         self.last_refill = now
#
#         if self.tokens >= amount:
#             self.tokens -= amount
#             return True
#         return False


class TokenBucketManager:
    def __init__(self, redis_client: Redis, capacity: int = 20, refill_rate: float = 5.0):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis = redis_client
        self.RATE_LIMIT_PREFIX = "rate_limit:"

        # Lua script for preventing race condition
        self.lua_script = self.redis.register_script(
            """
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            local amount = tonumber(ARGV[4])
            
            local data = redis.call('hgetall', key)
            local tokens
            local last_refill
            
            if #data == 0 then
                tokens = capacity
                last_refill = now
            else
                local bucket = {}
                for i=1, #data, 2 do
                    bucket[data[i]] = data[i+1]
                end
                
                tokens = tonumber(bucket['tokens'])
                last_refill = tonumber(bucket['last_refill'])
                
                local elapsed = now - last_refill
                tokens = math.min(capacity, tokens + math.floor(refill_rate * elapsed))
            end
                
            if tokens >= amount then
                tokens = tokens - amount
                redis.call('hset', key, 'tokens', tokens, 'last_refill', now)
                redis.call("expire", key, 120) 
                return 1
            else
                redis.call('hset', key, 'tokens', tokens, 'last_refill', now)
                redis.call("expire", key, 120) 
                return 0
            end
            
            """
        )

    async def consume(self, user_id: UUID, ip: str, amount: int = 1) -> bool:
        log.info("Consuming...")
        key = None
        if user_id:
            key = f"{self.RATE_LIMIT_PREFIX}:user:{str(user_id)}"
        elif ip:
            key = f"{self.RATE_LIMIT_PREFIX}:ip:{ip}"

        log.info(f"Key: {key}")

        if not key:
            raise ValueError("user_id or ip must be provided for rate limiting")

        now = time.time()
        data = await self.redis.hgetall(key)
        log.info(data)
        result = await self.lua_script(
            keys=[key],
            args=[self.capacity, self.refill_rate, now, amount]
        )
        return bool(result)

    # async def consume(self, user_id: UUID, ip: str, amount: int = 1) -> bool:
    #     log.info("Consuming...")
    #     key = None
    #     if user_id:
    #         key = f"{self.RATE_LIMIT_PREFIX}user:{str(user_id)}"
    #     elif ip:
    #         key = f"{self.RATE_LIMIT_PREFIX}ip:{ip}"
    #
    #     log.info(f"Key: {key}")
    #
    #     if not key:
    #         raise Exception
    #
    #     exists = await self.redis.exists(key)
    #     if not exists:
    #         await self.redis.hset(key, mapping={
    #             "tokens": self.capacity,
    #             "last_refill": int(time.time())
    #         })
    #
    #     data = await self.redis.hgetall(key)
    #     log.info(f"Before: {data}")
    #
    #     now = time.time()
    #     tokens = int(data["tokens"])
    #     last_refill = float(data["last_refill"])
    #
    #     elapsed = now - last_refill
    #     tokens = min(self.capacity, tokens + int(self.refill_rate * elapsed))
    #
    #     if tokens >= amount:
    #         tokens -= amount
    #         new_data = {
    #             "tokens": tokens,
    #             "last_refill": now
    #         }
    #         log.info(f"After: {new_data}")
    #         await self.redis.hset(key, mapping=new_data)
    #         return True
    #     return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        manager = request.app.state.token_bucket_manager

        auth_header = request.headers.get("Authorization")
        user_id = None
        client_ip = None
        if auth_header and auth_header.startswith("Bearer "):
            user_id = await helper.extract_user_from_token(auth_header.split(" ")[1])

        if request.client:
            client_ip = request.client.host

        if not await manager.consume(user_id=user_id, ip=client_ip):
            return JSONResponse({"detail": "Too Many Requests"}, status_code=429)

        return await call_next(request)







