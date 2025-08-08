import asyncio
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Request
import jwt
from passlib.context import CryptContext
from tanin.core.config import settings
from tanin.core.database import AsyncSessionDep
from tanin.repository.user_repo import UserRepository
from tanin.schemas.user_schema import ActiveUser
from fastapi import HTTPException, status, WebSocket

from tanin.utils.helper import extract_user_from_token
from tanin.utils import logger
from tanin.utils.logger import Module

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=11)

ALGORITHM = "HS256"

logger = logger.get_logger(Module.SECURITY)

async def get_current_active_user(request: Request, session: AsyncSessionDep) -> ActiveUser:
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        user_repo = UserRepository(session)
        user = await user_repo.get_user_by_id(UUID(await extract_user_from_token(token.split(" ")[1])))
        if user:
            return ActiveUser(
                id=user.id,
                display_name=user.display_name,
                is_anonymous=False,
                avatar=user.avatar
            )

    client_id = request.headers.get('X-Client-ID')
    if client_id:
        try:
            validated_client_id = UUID(client_id)
            return ActiveUser(
                id=validated_client_id,
                display_name='Stranger',
                is_anonymous=True
            )
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-Client-ID format")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


async def get_current_active_user_ws(websocket: WebSocket, session: AsyncSessionDep):
    auth_header = websocket.headers.get('Authorization')
    client_id_header = websocket.headers.get('X-Client-ID')

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        try:
            user_repo = UserRepository(session)
            user = await user_repo.get_user_by_id(UUID(await extract_user_from_token(token.split(" ")[1])))

            if user:
                return ActiveUser(
                    id=user.id,
                    display_name=user.display_name,
                    is_anonymous=False,
                    avatar=user.avatar
                )
        except Exception as e:
            logger.warning(f"Token invalid or user not found: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
            return

    if client_id_header:
        try:
            validated_client_id = UUID(client_id_header)
            return ActiveUser(
                id=validated_client_id,
                display_name='Stranger',
                is_anonymous=True
            )
        except ValueError:
            logger.warning("Invalid anonymous client ID format")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid X-Client-ID format")
            return

    logger.warning("No authentication headers found")
    await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication credentials")


def _create_access_token_sync(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _get_password_hash_sync(password: str) -> str:
    return pwd_context.hash(password)


def generate_token(length: int = 32):
    return secrets.token_urlsafe(length)


def get_token_hash(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def is_valid_token(hash_token, plain_token):
    new_hash_token = get_token_hash(plain_token)
    return hmac.compare_digest(hash_token, new_hash_token)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _verify_password_sync,
        plain_password,
        hashed_password
    )


async def get_password_hash(password: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _get_password_hash_sync,
        password
    )
