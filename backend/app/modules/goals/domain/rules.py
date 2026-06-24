from datetime import date
from decimal import Decimal

from app.core.exceptions.base import AppException


def ensure_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise AppException(f"{field_name} cannot be empty", code="INVALID_TEXT_FIELD", status_code=422)


def ensure_exam_date_not_past(exam_date: date) -> None:
    if exam_date < date.today():
        raise AppException("exam_date should not be in the past", code="INVALID_EXAM_DATE", status_code=422)


def ensure_rating(value: int, field_name: str) -> None:
    if value < 1 or value > 5:
        raise AppException(f"{field_name} must be between 1 and 5", code="INVALID_RATING", status_code=422)


def ensure_positive_decimal(value: Decimal | None, field_name: str) -> None:
    if value is not None and value <= 0:
        raise AppException(f"{field_name} must be positive", code="INVALID_DECIMAL", status_code=422)

