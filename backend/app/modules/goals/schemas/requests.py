from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class GoalCreateRequest(BaseModel):
    title: str
    description: str | None = None
    exam_date: date
    target_score: str | None = None


class GoalUpdateRequest(BaseModel):
    title: str
    description: str | None = None
    exam_date: date
    target_score: str | None = None


class SubjectCreateRequest(BaseModel):
    name: str
    description: str | None = None
    priority: int = 3


class TopicCreateRequest(BaseModel):
    name: str
    description: str | None = None
    difficulty: int = 3
    priority: int = 3
    estimated_hours: Decimal | None = None
    is_manually_marked_weak: bool = False

