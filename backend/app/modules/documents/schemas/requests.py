from uuid import UUID

from pydantic import BaseModel


class DocumentListQuery(BaseModel):
    goal_id: UUID | None = None

