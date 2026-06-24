from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.infrastructure_models import AvailabilityWindow, StudentProfile, User
from app.modules.users.repositories.interfaces import (
    AvailabilityWindowRepository,
    StudentProfileRepository,
    UserRepository,
)


class PostgresUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: User) -> User:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> User | None:
        return self.session.get(User, entity_id)

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def delete(self, entity: User) -> None:
        self.session.delete(entity)


class PostgresStudentProfileRepository(StudentProfileRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: StudentProfile) -> StudentProfile:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> StudentProfile | None:
        return self.session.get(StudentProfile, entity_id)

    def get_by_user_id(self, user_id: UUID) -> StudentProfile | None:
        return self.session.scalar(select(StudentProfile).where(StudentProfile.user_id == user_id))

    def delete(self, entity: StudentProfile) -> None:
        self.session.delete(entity)


class PostgresAvailabilityWindowRepository(AvailabilityWindowRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: AvailabilityWindow) -> AvailabilityWindow:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> AvailabilityWindow | None:
        return self.session.get(AvailabilityWindow, entity_id)

    def list_by_user_id(self, user_id: UUID) -> list[AvailabilityWindow]:
        return list(self.session.scalars(select(AvailabilityWindow).where(AvailabilityWindow.user_id == user_id)))

    def delete(self, entity: AvailabilityWindow) -> None:
        self.session.delete(entity)

