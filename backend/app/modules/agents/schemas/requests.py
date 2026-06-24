from uuid import UUID

from pydantic import BaseModel


class ExplainStudyPlanRequest(BaseModel):
    version_id: UUID | None = None

