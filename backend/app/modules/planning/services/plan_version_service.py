from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.planning.exceptions import PlanNotFoundError, PlanVersionNotFoundError
from app.modules.planning.infrastructure_models import StudyPlan, StudyPlanVersion
from app.modules.planning.repositories.postgres_repository import PostgresStudyPlanRepository, PostgresStudyPlanVersionRepository
from app.modules.planning.schemas.responses import PlanVersionResponse


class PlanVersionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.plans = PostgresStudyPlanRepository(session)
        self.versions = PostgresStudyPlanVersionRepository(session)

    def get_plan_for_user(self, user_id: UUID, plan_id: UUID) -> StudyPlan:
        plan = self.plans.get_by_id(plan_id)
        if plan is None or plan.user_id != user_id or plan.status == "archived":
            raise PlanNotFoundError()
        return plan

    def get_active_version(self, user_id: UUID, plan_id: UUID) -> StudyPlanVersion:
        self.get_plan_for_user(user_id, plan_id)
        version = self.versions.get_active_by_plan_id(plan_id)
        if version is None or version.user_id != user_id:
            raise PlanVersionNotFoundError()
        return version

    def list_versions(self, user_id: UUID, plan_id: UUID) -> list[PlanVersionResponse]:
        self.get_plan_for_user(user_id, plan_id)
        return [self._to_response(version) for version in self.versions.list_by_plan_id(plan_id) if version.user_id == user_id]

    def get_version(self, user_id: UUID, plan_id: UUID, version_id: UUID) -> PlanVersionResponse:
        self.get_plan_for_user(user_id, plan_id)
        version = self.versions.get_by_id(version_id)
        if version is None or version.study_plan_id != plan_id or version.user_id != user_id:
            raise PlanVersionNotFoundError()
        return self._to_response(version)

    @staticmethod
    def _to_response(version: StudyPlanVersion) -> PlanVersionResponse:
        return PlanVersionResponse(
            version_id=version.id,
            version_number=version.version_number,
            version_reason=version.version_reason,
            generated_by=version.generated_by,
            summary=version.summary,
            is_active=version.is_active,
            created_at=version.created_at,
        )

