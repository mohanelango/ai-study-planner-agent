from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True)
class PlannerGoal:
    id: UUID
    title: str
    exam_date: date


@dataclass(frozen=True)
class PlannerTopic:
    id: UUID
    subject_id: UUID
    name: str
    difficulty: int
    priority: int
    estimated_hours: Decimal | None = None


@dataclass(frozen=True)
class PlannerAvailabilityWindow:
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool = True


@dataclass
class GeneratedTask:
    topic_id: UUID | None
    subject_id: UUID | None
    title: str
    description: str | None
    task_type: str
    planned_duration_minutes: int
    sort_order: int


@dataclass
class GeneratedSession:
    temp_id: UUID = field(default_factory=uuid4)
    session_date: date = field(default_factory=date.today)
    start_time: time | None = None
    end_time: time | None = None
    planned_duration_minutes: int = 0
    session_type: str = "study"
    tasks: list[GeneratedTask] = field(default_factory=list)


@dataclass
class PlannerResult:
    summary: str
    warnings: list[str]
    sessions: list[GeneratedSession]

    @property
    def total_tasks(self) -> int:
        return sum(len(session.tasks) for session in self.sessions)

