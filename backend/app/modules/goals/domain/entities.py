from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GoalOwnership:
    user_id: UUID
    goal_id: UUID

