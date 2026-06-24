from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.goals.exceptions import GoalNotFoundError
from app.modules.goals.repositories.postgres_repository import PostgresStudyGoalRepository, PostgresTopicRepository
from app.modules.planning.domain.planner import RuleBasedPlanner
from app.modules.planning.domain.rules import PlanningDomainError
from app.modules.planning.domain.value_objects import PlannerAvailabilityWindow, PlannerGoal, PlannerResult, PlannerTopic
from app.modules.planning.exceptions import PlanningValidationError
from app.modules.users.repositories.postgres_repository import PostgresAvailabilityWindowRepository, PostgresStudentProfileRepository


class ScheduleGenerationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.goals = PostgresStudyGoalRepository(session)
        self.topics = PostgresTopicRepository(session)
        self.availability = PostgresAvailabilityWindowRepository(session)
        self.profiles = PostgresStudentProfileRepository(session)
        self.planner = RuleBasedPlanner()

    def generate(self, user_id: UUID, goal_id: UUID, preferred_session_minutes: int, include_revision_sessions: bool) -> PlannerResult:
        goal = self.goals.get_by_id(goal_id)
        if goal is None or goal.user_id != user_id or goal.status == "archived":
            raise GoalNotFoundError()

        profile = self.profiles.get_by_user_id(user_id)
        session_minutes = preferred_session_minutes or (profile.preferred_study_duration_minutes if profile else 60) or 60

        topics = [topic for topic in self.topics.list_by_goal_id(goal_id) if topic.user_id == user_id]
        windows = [window for window in self.availability.list_by_user_id(user_id) if window.is_active]

        try:
            return self.planner.generate(
                goal=PlannerGoal(id=goal.id, title=goal.title, exam_date=goal.exam_date),
                topics=[
                    PlannerTopic(
                        id=topic.id,
                        subject_id=topic.subject_id,
                        name=topic.name,
                        difficulty=topic.difficulty,
                        priority=topic.priority,
                        estimated_hours=topic.estimated_hours,
                    )
                    for topic in topics
                ],
                availability_windows=[
                    PlannerAvailabilityWindow(
                        day_of_week=window.day_of_week,
                        start_time=window.start_time,
                        end_time=window.end_time,
                        is_active=window.is_active,
                    )
                    for window in windows
                ],
                preferred_session_minutes=session_minutes,
                include_revision_sessions=include_revision_sessions,
            )
        except PlanningDomainError as exc:
            raise PlanningValidationError(str(exc)) from exc

