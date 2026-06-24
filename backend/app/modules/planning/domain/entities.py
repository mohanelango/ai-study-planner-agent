from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PlanIdentity:
    study_plan_id: UUID
    active_version_id: UUID

