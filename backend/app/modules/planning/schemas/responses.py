from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StudyPlanGenerationResponse(BaseModel):
    study_plan_id: UUID
    active_version_id: UUID
    version_number: int
    summary: str
    warnings: list[str]
    total_sessions: int
    total_tasks: int


class TaskResponse(BaseModel):
    task_id: UUID
    topic_id: UUID | None
    subject_id: UUID | None
    title: str
    description: str | None
    task_type: str
    status: str
    planned_duration_minutes: int
    sort_order: int


class SessionResponse(BaseModel):
    session_id: UUID
    session_date: date
    start_time: time | None
    end_time: time | None
    session_type: str
    status: str
    planned_duration_minutes: int
    tasks: list[TaskResponse]


class StudyPlanCalendarResponse(BaseModel):
    plan_id: UUID
    version_id: UUID
    sessions: list[SessionResponse]


class TodayTasksResponse(BaseModel):
    date: date
    sessions: list[SessionResponse]


class PlanVersionResponse(BaseModel):
    version_id: UUID
    version_number: int
    version_reason: str
    generated_by: str
    summary: str | None
    is_active: bool
    created_at: datetime


class StudyPlanOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    study_plan_id: UUID
    goal_id: UUID
    title: str
    status: str
    active_version_id: UUID | None
    active_version: PlanVersionResponse | None
    created_at: datetime
    updated_at: datetime

