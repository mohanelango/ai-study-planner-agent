from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool


class RegisterUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: str
    full_name: str | None
    is_active: bool


class LoginUser(BaseModel):
    id: UUID
    email: str
    full_name: str | None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: LoginUser


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    education_level: str | None
    timezone: str
    preferred_study_duration_minutes: int | None
    learning_style: str | None
    daily_goal_minutes: int | None
    created_at: datetime
    updated_at: datetime


class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime

