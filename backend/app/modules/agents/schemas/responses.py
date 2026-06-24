from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StudyPlanExplanationPayload(BaseModel):
    headline: str
    summary: str
    priority_rationale: list[str] = Field(default_factory=list)
    schedule_rationale: list[str] = Field(default_factory=list)
    risk_warnings: list[str] = Field(default_factory=list)
    next_best_actions: list[str] = Field(default_factory=list)


class StudyPlanExplanationResponse(StudyPlanExplanationPayload):
    agent_run_id: UUID
    study_plan_id: UUID
    version_id: UUID
    generated_at: datetime

