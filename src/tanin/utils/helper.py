from datetime import timedelta, datetime, timezone
from typing import Optional

import jwt

from tanin.core.config import settings
from tanin.schemas.token_schema import TokenPayload
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession


async def extract_user_from_token(token: str):
    from tanin.core import security
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data.sub


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    from tanin.core import security
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.SECRET_KEY,
        algorithm=security.ALGORITHM
    )

    return encoded_jwt
