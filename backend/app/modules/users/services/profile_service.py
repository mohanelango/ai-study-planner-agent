from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.users.domain.rules import ensure_day_of_week, ensure_positive, ensure_time_window
from app.modules.users.exceptions import AvailabilityNotFoundError, ProfileAlreadyExistsError, ProfileNotFoundError
from app.modules.users.infrastructure_models import AvailabilityWindow, StudentProfile
from app.modules.users.repositories.postgres_repository import (
    PostgresAvailabilityWindowRepository,
    PostgresStudentProfileRepository,
)
from app.modules.users.schemas.requests import AvailabilityRequest, ProfileRequest


class ProfileService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.profiles = PostgresStudentProfileRepository(session)
        self.availability = PostgresAvailabilityWindowRepository(session)

    def create_profile(self, user_id: UUID, request: ProfileRequest) -> StudentProfile:
        self._validate_profile(request)
        if self.profiles.get_by_user_id(user_id):
            raise ProfileAlreadyExistsError()

        profile = StudentProfile(user_id=user_id, **request.model_dump())
        self.profiles.add(profile)
        self.session.commit()
        return profile

    def get_profile(self, user_id: UUID) -> StudentProfile:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError()
        return profile

    def update_profile(self, user_id: UUID, request: ProfileRequest) -> StudentProfile:
        self._validate_profile(request)
        profile = self.get_profile(user_id)
        for field, value in request.model_dump().items():
            setattr(profile, field, value)
        self.session.commit()
        return profile

    def create_availability(self, user_id: UUID, request: AvailabilityRequest) -> AvailabilityWindow:
        ensure_day_of_week(request.day_of_week)
        ensure_time_window(request.start_time, request.end_time)
        window = AvailabilityWindow(user_id=user_id, **request.model_dump())
        self.availability.add(window)
        self.session.commit()
        return window

    def list_availability(self, user_id: UUID) -> list[AvailabilityWindow]:
        return self.availability.list_by_user_id(user_id)

    def delete_availability(self, user_id: UUID, availability_id: UUID) -> None:
        window = self.availability.get_by_id(availability_id)
        if window is None or window.user_id != user_id:
            raise AvailabilityNotFoundError()
        self.availability.delete(window)
        self.session.commit()

    @staticmethod
    def _validate_profile(request: ProfileRequest) -> None:
        ensure_positive(request.preferred_study_duration_minutes, "preferred_study_duration_minutes")
        ensure_positive(request.daily_goal_minutes, "daily_goal_minutes")

