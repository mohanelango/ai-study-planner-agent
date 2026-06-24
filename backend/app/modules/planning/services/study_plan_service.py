from collections import defaultdict
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.goals.exceptions import GoalNotFoundError
from app.modules.goals.repositories.postgres_repository import PostgresStudyGoalRepository
from app.modules.planning.exceptions import DuplicateActivePlanError, PlanNotFoundError, PlanVersionNotFoundError
from app.modules.planning.infrastructure_models import StudyPlan, StudyPlanVersion, StudySession, StudyTask
from app.modules.planning.repositories.postgres_repository import (
    PostgresStudyPlanRepository,
    PostgresStudyPlanVersionRepository,
    PostgresStudySessionRepository,
    PostgresStudyTaskRepository,
)
from app.modules.planning.schemas.requests import GenerateStudyPlanRequest
from app.modules.planning.schemas.responses import (
    PlanVersionResponse,
    SessionResponse,
    StudyPlanCalendarResponse,
    StudyPlanGenerationResponse,
    StudyPlanOverviewResponse,
    TaskResponse,
    TodayTasksResponse,
)
from app.modules.planning.services.plan_version_service import PlanVersionService
from app.modules.planning.services.schedule_generation_service import ScheduleGenerationService


class StudyPlanService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.goals = PostgresStudyGoalRepository(session)
        self.plans = PostgresStudyPlanRepository(session)
        self.versions = PostgresStudyPlanVersionRepository(session)
        self.sessions = PostgresStudySessionRepository(session)
        self.tasks = PostgresStudyTaskRepository(session)
        self.version_service = PlanVersionService(session)

    def generate_plan(self, user_id: UUID, request: GenerateStudyPlanRequest) -> StudyPlanGenerationResponse:
        goal = self.goals.get_by_id(request.goal_id)
        if goal is None or goal.user_id != user_id or goal.status == "archived":
            raise GoalNotFoundError()
        if self.plans.get_active_by_goal_id(goal.id):
            raise DuplicateActivePlanError()

        result = ScheduleGenerationService(self.session).generate(
            user_id=user_id,
            goal_id=goal.id,
            preferred_session_minutes=request.preferred_session_minutes,
            include_revision_sessions=request.include_revision_sessions,
        )

        try:
            study_plan = self.plans.add(
                StudyPlan(
                    goal_id=goal.id,
                    user_id=user_id,
                    title=(request.plan_title.strip() if request.plan_title else f"Study Plan: {goal.title}"),
                    status="active",
                )
            )
            version = self.versions.add(
                StudyPlanVersion(
                    study_plan_id=study_plan.id,
                    goal_id=goal.id,
                    user_id=user_id,
                    version_number=1,
                    version_reason="initial_generation",
                    generated_by="system",
                    summary=result.summary,
                    is_active=True,
                )
            )
            study_plan.active_version_id = version.id

            session_rows: list[StudySession] = []
            for generated_session in result.sessions:
                row = StudySession(
                    study_plan_version_id=version.id,
                    study_plan_id=study_plan.id,
                    goal_id=goal.id,
                    user_id=user_id,
                    session_date=generated_session.session_date,
                    start_time=generated_session.start_time,
                    end_time=generated_session.end_time,
                    planned_duration_minutes=generated_session.planned_duration_minutes,
                    session_type=generated_session.session_type,
                    status="scheduled",
                )
                session_rows.append(row)
            self.sessions.add_many(session_rows)

            task_rows: list[StudyTask] = []
            for row, generated_session in zip(session_rows, result.sessions, strict=True):
                for generated_task in generated_session.tasks:
                    task_rows.append(
                        StudyTask(
                            study_session_id=row.id,
                            topic_id=generated_task.topic_id,
                            subject_id=generated_task.subject_id,
                            user_id=user_id,
                            title=generated_task.title,
                            description=generated_task.description,
                            task_type=generated_task.task_type,
                            planned_duration_minutes=generated_task.planned_duration_minutes,
                            status="pending",
                            sort_order=generated_task.sort_order,
                        )
                    )
            self.tasks.add_many(task_rows)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return StudyPlanGenerationResponse(
            study_plan_id=study_plan.id,
            active_version_id=version.id,
            version_number=1,
            summary=result.summary,
            warnings=result.warnings,
            total_sessions=len(session_rows),
            total_tasks=len(task_rows),
        )

    def get_overview(self, user_id: UUID, plan_id: UUID) -> StudyPlanOverviewResponse:
        plan = self._get_plan_for_user(user_id, plan_id)
        active_version = self.versions.get_active_by_plan_id(plan.id)
        return StudyPlanOverviewResponse(
            study_plan_id=plan.id,
            goal_id=plan.goal_id,
            title=plan.title,
            status=plan.status,
            active_version_id=plan.active_version_id,
            active_version=PlanVersionService._to_response(active_version) if active_version else None,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )

    def get_calendar(self, user_id: UUID, plan_id: UUID, start_date: date | None, end_date: date | None, version_id: UUID | None = None) -> StudyPlanCalendarResponse:
        plan = self._get_plan_for_user(user_id, plan_id)
        version = self._resolve_version(user_id, plan.id, version_id)
        sessions = [session for session in self.sessions.list_by_plan_id_date_range(plan.id, start_date, end_date) if session.study_plan_version_id == version.id]
        return StudyPlanCalendarResponse(plan_id=plan.id, version_id=version.id, sessions=self._sessions_to_response(sessions))

    def get_today(self, user_id: UUID, plan_id: UUID) -> TodayTasksResponse:
        plan = self._get_plan_for_user(user_id, plan_id)
        version = self._resolve_version(user_id, plan.id, None)
        today = date.today()
        sessions = [session for session in self.sessions.list_today_by_user_id(user_id, today) if session.study_plan_id == plan.id and session.study_plan_version_id == version.id]
        return TodayTasksResponse(date=today, sessions=self._sessions_to_response(sessions))

    def _get_plan_for_user(self, user_id: UUID, plan_id: UUID) -> StudyPlan:
        plan = self.plans.get_by_id(plan_id)
        if plan is None or plan.user_id != user_id or plan.status == "archived":
            raise PlanNotFoundError()
        return plan

    def _resolve_version(self, user_id: UUID, plan_id: UUID, version_id: UUID | None) -> StudyPlanVersion:
        if version_id is None:
            return self.version_service.get_active_version(user_id, plan_id)
        version = self.versions.get_by_id(version_id)
        if version is None or version.study_plan_id != plan_id or version.user_id != user_id:
            raise PlanVersionNotFoundError()
        return version

    def _sessions_to_response(self, sessions: list[StudySession]) -> list[SessionResponse]:
        task_rows = self.tasks.list_by_session_ids([session.id for session in sessions])
        tasks_by_session: dict[UUID, list[StudyTask]] = defaultdict(list)
        for task in task_rows:
            tasks_by_session[task.study_session_id].append(task)

        return [
            SessionResponse(
                session_id=session.id,
                session_date=session.session_date,
                start_time=session.start_time,
                end_time=session.end_time,
                session_type=session.session_type,
                status=session.status,
                planned_duration_minutes=session.planned_duration_minutes,
                tasks=[
                    TaskResponse(
                        task_id=task.id,
                        topic_id=task.topic_id,
                        subject_id=task.subject_id,
                        title=task.title,
                        description=task.description,
                        task_type=task.task_type,
                        status=task.status,
                        planned_duration_minutes=task.planned_duration_minutes,
                        sort_order=task.sort_order,
                    )
                    for task in tasks_by_session[session.id]
                ],
            )
            for session in sessions
        ]
