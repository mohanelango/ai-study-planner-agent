from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.modules.planning.infrastructure_models import StudyPlan, StudyPlanVersion, StudySession, StudyTask
from app.shared.base.base_repository import BaseRepository


class StudyPlanRepository(BaseRepository[StudyPlan], ABC):
    @abstractmethod
    def get_active_by_goal_id(self, goal_id: UUID) -> StudyPlan | None: ...

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[StudyPlan]: ...

    @abstractmethod
    def update_active_version(self, study_plan: StudyPlan, version_id: UUID) -> StudyPlan: ...

    @abstractmethod
    def archive_existing_active_for_goal(self, goal_id: UUID) -> None: ...


class StudyPlanVersionRepository(BaseRepository[StudyPlanVersion], ABC):
    @abstractmethod
    def list_by_plan_id(self, plan_id: UUID) -> list[StudyPlanVersion]: ...

    @abstractmethod
    def get_active_by_plan_id(self, plan_id: UUID) -> StudyPlanVersion | None: ...

    @abstractmethod
    def deactivate_versions_for_plan(self, plan_id: UUID) -> None: ...


class StudySessionRepository(ABC):
    @abstractmethod
    def add_many(self, entities: list[StudySession]) -> list[StudySession]: ...

    @abstractmethod
    def list_by_version_id(self, version_id: UUID) -> list[StudySession]: ...

    @abstractmethod
    def list_by_plan_id_date_range(self, plan_id: UUID, start_date: date | None, end_date: date | None) -> list[StudySession]: ...

    @abstractmethod
    def list_today_by_user_id(self, user_id: UUID, current_date: date) -> list[StudySession]: ...


class StudyTaskRepository(ABC):
    @abstractmethod
    def add_many(self, entities: list[StudyTask]) -> list[StudyTask]: ...

    @abstractmethod
    def list_by_session_ids(self, session_ids: list[UUID]) -> list[StudyTask]: ...

    @abstractmethod
    def list_today_by_user_id(self, user_id: UUID, current_date: date) -> list[StudyTask]: ...

