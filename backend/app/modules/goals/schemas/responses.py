from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    exam_date: date
    target_score: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal_id: UUID
    name: str
    description: str | None
    priority: int


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_id: UUID
    goal_id: UUID
    name: str
    description: str | None
    difficulty: int
    priority: int
    estimated_hours: Decimal | None
    is_manually_marked_weak: bool

