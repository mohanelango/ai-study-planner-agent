from datetime import time

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email address")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email address")
        return value


class ProfileRequest(BaseModel):
    education_level: str | None = None
    timezone: str = "Asia/Kolkata"
    preferred_study_duration_minutes: int | None = None
    learning_style: str | None = None
    daily_goal_minutes: int | None = None


class AvailabilityRequest(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time
