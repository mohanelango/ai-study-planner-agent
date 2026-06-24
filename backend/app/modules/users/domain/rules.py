from datetime import time

from app.core.exceptions.base import AppException


def normalize_email(email: str) -> str:
    return email.strip().lower()


def ensure_password_is_valid(password: str) -> None:
    if len(password) < 8:
        raise AppException("Password must be at least 8 characters long", code="WEAK_PASSWORD", status_code=422)


def ensure_positive(value: int | None, field_name: str) -> None:
    if value is not None and value <= 0:
        raise AppException(f"{field_name} must be positive", code="INVALID_PROFILE_VALUE", status_code=422)


def ensure_day_of_week(day_of_week: int) -> None:
    if day_of_week < 0 or day_of_week > 6:
        raise AppException("day_of_week must be between 0 and 6", code="INVALID_DAY_OF_WEEK", status_code=422)


def ensure_time_window(start_time: time, end_time: time) -> None:
    if start_time >= end_time:
        raise AppException("start_time must be before end_time", code="INVALID_TIME_WINDOW", status_code=422)

