from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.users.infrastructure_models import AvailabilityWindow, StudentProfile, User
from app.shared.base.base_repository import BaseRepository


class UserRepository(BaseRepository[User], ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError


class StudentProfileRepository(BaseRepository[StudentProfile], ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> StudentProfile | None:
        raise NotImplementedError


class AvailabilityWindowRepository(BaseRepository[AvailabilityWindow], ABC):
    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[AvailabilityWindow]:
        raise NotImplementedError

