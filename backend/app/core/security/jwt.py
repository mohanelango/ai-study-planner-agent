from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.core.config.settings import settings
from app.core.exceptions.base import AppException


def create_access_token(user_id: UUID) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expires_at, "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        subject = payload.get("sub")
        token_type = payload.get("type")
        if not subject or token_type != "access":
            raise AppException("Invalid authentication token", code="INVALID_TOKEN", status_code=401)
        return UUID(subject)
    except (JWTError, ValueError) as exc:
        raise AppException("Invalid authentication token", code="INVALID_TOKEN", status_code=401) from exc

