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
