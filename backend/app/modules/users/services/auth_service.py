from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.core.security.jwt import create_access_token
from app.core.security.password_hasher import hash_password, verify_password
from app.modules.users.domain.rules import ensure_password_is_valid, normalize_email
from app.modules.users.exceptions import DuplicateEmailError, InvalidCredentialsError
from app.modules.users.infrastructure_models import User
from app.modules.users.repositories.postgres_repository import PostgresUserRepository
from app.modules.users.schemas.requests import LoginRequest, RegisterRequest
from app.modules.users.schemas.responses import LoginResponse, LoginUser, RegisterUserResponse


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = PostgresUserRepository(session)

    def register(self, request: RegisterRequest) -> RegisterUserResponse:
        email = normalize_email(str(request.email))
        ensure_password_is_valid(request.password)
        if self.users.get_by_email(email):
            raise DuplicateEmailError()

        user = User(
            email=email,
            password_hash=hash_password(request.password),
            full_name=request.full_name.strip() if request.full_name else None,
        )
        try:
            self.users.add(user)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise DuplicateEmailError() from exc

        return RegisterUserResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )

    def login(self, request: LoginRequest) -> LoginResponse:
        email = normalize_email(str(request.email))
        user = self.users.get_by_email(email)
        if user is None or not verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()

        return LoginResponse(
            access_token=create_access_token(user.id),
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=LoginUser(id=user.id, email=user.email, full_name=user.full_name),
        )

