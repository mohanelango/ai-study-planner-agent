from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions.base import AppException
from app.core.security.jwt import decode_access_token
from app.infrastructure.database.session import get_db
from app.modules.users.infrastructure_models import User
from app.modules.users.repositories.postgres_repository import PostgresUserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppException("Authentication required", code="AUTHENTICATION_REQUIRED", status_code=401)

    user_id = decode_access_token(credentials.credentials)
    user = PostgresUserRepository(db).get_by_id(user_id)
    if user is None:
        raise AppException("User not found", code="USER_NOT_FOUND", status_code=401)
    if not user.is_active:
        raise AppException("User account is inactive", code="USER_INACTIVE", status_code=403)
    return user

