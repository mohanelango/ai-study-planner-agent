from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security.auth_dependencies import get_current_user
from app.infrastructure.database.session import get_db
from app.modules.users.infrastructure_models import User
from app.modules.users.schemas.requests import AvailabilityRequest, LoginRequest, ProfileRequest, RegisterRequest
from app.modules.users.schemas.responses import AvailabilityResponse, LoginResponse, ProfileResponse, RegisterUserResponse, UserPublic
from app.modules.users.services.auth_service import AuthService
from app.modules.users.services.profile_service import ProfileService

router = APIRouter(tags=["users"])


def success(message: str, data: object | None = None) -> dict:
    return {"success": True, "message": message, "data": data if data is not None else {}}


@router.post("/auth/register")
def register(request: RegisterRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    data: RegisterUserResponse = AuthService(db).register(request)
    return success("User registered successfully", data.model_dump(mode="json"))


@router.post("/auth/login")
def login(request: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    data: LoginResponse = AuthService(db).login(request)
    return success("Login successful", data.model_dump(mode="json"))


@router.get("/auth/me")
def me(current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    data = UserPublic.model_validate(current_user)
    return success("Current user fetched successfully", data.model_dump(mode="json"))


@router.post("/profiles")
def create_profile(
    request: ProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    profile = ProfileService(db).create_profile(current_user.id, request)
    data = ProfileResponse.model_validate(profile)
    return success("Profile created successfully", data.model_dump(mode="json"))


@router.get("/profiles/me")
def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    profile = ProfileService(db).get_profile(current_user.id)
    data = ProfileResponse.model_validate(profile)
    return success("Profile fetched successfully", data.model_dump(mode="json"))


@router.put("/profiles/me")
def update_profile(
    request: ProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    profile = ProfileService(db).update_profile(current_user.id, request)
    data = ProfileResponse.model_validate(profile)
    return success("Profile updated successfully", data.model_dump(mode="json"))


@router.post("/availability")
def create_availability(
    request: AvailabilityRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    window = ProfileService(db).create_availability(current_user.id, request)
    data = AvailabilityResponse.model_validate(window)
    return success("Availability window created successfully", data.model_dump(mode="json"))


@router.get("/availability")
def list_availability(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    windows = ProfileService(db).list_availability(current_user.id)
    data = [AvailabilityResponse.model_validate(window).model_dump(mode="json") for window in windows]
    return success("Availability windows fetched successfully", data)


@router.delete("/availability/{availability_id}")
def delete_availability(
    availability_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    ProfileService(db).delete_availability(current_user.id, availability_id)
    return success("Availability window deleted successfully")

