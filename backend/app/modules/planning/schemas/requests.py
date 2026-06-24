from uuid import UUID

from pydantic import BaseModel, Field


class GenerateStudyPlanRequest(BaseModel):
    goal_id: UUID
    plan_title: str | None = None
    include_revision_sessions: bool = True
    preferred_session_minutes: int = Field(default=60, ge=30, le=180)

