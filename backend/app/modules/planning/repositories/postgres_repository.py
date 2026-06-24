from datetime import date
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.planning.infrastructure_models import StudyPlan, StudyPlanVersion, StudySession, StudyTask
from app.modules.planning.repositories.interfaces import (
    StudyPlanRepository,
    StudyPlanVersionRepository,
    StudySessionRepository,
    StudyTaskRepository,
)


class PostgresStudyPlanRepository(StudyPlanRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: StudyPlan) -> StudyPlan:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> StudyPlan | None:
        return self.session.get(StudyPlan, entity_id)

    def get_active_by_goal_id(self, goal_id: UUID) -> StudyPlan | None:
        return self.session.scalar(select(StudyPlan).where(StudyPlan.goal_id == goal_id, StudyPlan.status == "active"))

    def list_by_user_id(self, user_id: UUID) -> list[StudyPlan]:
        return list(self.session.scalars(select(StudyPlan).where(StudyPlan.user_id == user_id)))

    def update_active_version(self, study_plan: StudyPlan, version_id: UUID) -> StudyPlan:
        study_plan.active_version_id = version_id
        self.session.flush()
        return study_plan

    def archive_existing_active_for_goal(self, goal_id: UUID) -> None:
        self.session.execute(update(StudyPlan).where(StudyPlan.goal_id == goal_id, StudyPlan.status == "active").values(status="archived"))

    def delete(self, entity: StudyPlan) -> None:
        self.session.delete(entity)


class PostgresStudyPlanVersionRepository(StudyPlanVersionRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: StudyPlanVersion) -> StudyPlanVersion:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> StudyPlanVersion | None:
        return self.session.get(StudyPlanVersion, entity_id)

    def list_by_plan_id(self, plan_id: UUID) -> list[StudyPlanVersion]:
        return list(self.session.scalars(select(StudyPlanVersion).where(StudyPlanVersion.study_plan_id == plan_id).order_by(StudyPlanVersion.version_number)))

    def get_active_by_plan_id(self, plan_id: UUID) -> StudyPlanVersion | None:
        return self.session.scalar(select(StudyPlanVersion).where(StudyPlanVersion.study_plan_id == plan_id, StudyPlanVersion.is_active.is_(True)))

    def deactivate_versions_for_plan(self, plan_id: UUID) -> None:
        self.session.execute(update(StudyPlanVersion).where(StudyPlanVersion.study_plan_id == plan_id).values(is_active=False))

    def delete(self, entity: StudyPlanVersion) -> None:
        self.session.delete(entity)


class PostgresStudySessionRepository(StudySessionRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_many(self, entities: list[StudySession]) -> list[StudySession]:
        self.session.add_all(entities)
        self.session.flush()
        return entities

    def list_by_version_id(self, version_id: UUID) -> list[StudySession]:
        return list(self.session.scalars(select(StudySession).where(StudySession.study_plan_version_id == version_id).order_by(StudySession.session_date, StudySession.start_time)))

    def list_by_plan_id_date_range(self, plan_id: UUID, start_date: date | None, end_date: date | None) -> list[StudySession]:
        query = select(StudySession).where(StudySession.study_plan_id == plan_id)
        if start_date:
            query = query.where(StudySession.session_date >= start_date)
        if end_date:
            query = query.where(StudySession.session_date <= end_date)
        return list(self.session.scalars(query.order_by(StudySession.session_date, StudySession.start_time)))

    def list_today_by_user_id(self, user_id: UUID, current_date: date) -> list[StudySession]:
        return list(self.session.scalars(select(StudySession).where(StudySession.user_id == user_id, StudySession.session_date == current_date).order_by(StudySession.start_time)))


class PostgresStudyTaskRepository(StudyTaskRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_many(self, entities: list[StudyTask]) -> list[StudyTask]:
        self.session.add_all(entities)
        self.session.flush()
        return entities

    def list_by_session_ids(self, session_ids: list[UUID]) -> list[StudyTask]:
        if not session_ids:
            return []
        return list(self.session.scalars(select(StudyTask).where(StudyTask.study_session_id.in_(session_ids)).order_by(StudyTask.sort_order)))

    def list_today_by_user_id(self, user_id: UUID, current_date: date) -> list[StudyTask]:
        query = (
            select(StudyTask)
            .join(StudySession, StudyTask.study_session_id == StudySession.id)
            .where(StudyTask.user_id == user_id, StudySession.session_date == current_date)
            .order_by(StudySession.start_time, StudyTask.sort_order)
        )
        return list(self.session.scalars(query))

