from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.goals.infrastructure_models import StudyGoal, Subject, Topic
from app.shared.base.base_repository import BaseRepository


class StudyGoalRepository(BaseRepository[StudyGoal], ABC):
    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[StudyGoal]:
        raise NotImplementedError


class SubjectRepository(BaseRepository[Subject], ABC):
    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Subject]:
        raise NotImplementedError

    @abstractmethod
    def list_by_goal_id(self, goal_id: UUID) -> list[Subject]:
        raise NotImplementedError


class TopicRepository(BaseRepository[Topic], ABC):
    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Topic]:
        raise NotImplementedError

    @abstractmethod
    def list_by_goal_id(self, goal_id: UUID) -> list[Topic]:
        raise NotImplementedError

    @abstractmethod
    def list_by_subject_id(self, subject_id: UUID) -> list[Topic]:
        raise NotImplementedError

