from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.goals.domain.rules import ensure_exam_date_not_past, ensure_non_empty, ensure_positive_decimal, ensure_rating
from app.modules.goals.exceptions import GoalNotFoundError, SubjectNotFoundError
from app.modules.goals.infrastructure_models import StudyGoal, Subject, Topic
from app.modules.goals.repositories.postgres_repository import PostgresStudyGoalRepository, PostgresSubjectRepository, PostgresTopicRepository
from app.modules.goals.schemas.requests import GoalCreateRequest, GoalUpdateRequest, SubjectCreateRequest, TopicCreateRequest


class GoalService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.goals = PostgresStudyGoalRepository(session)
        self.subjects = PostgresSubjectRepository(session)
        self.topics = PostgresTopicRepository(session)

    def create_goal(self, user_id: UUID, request: GoalCreateRequest) -> StudyGoal:
        self._validate_goal(request.title, request.exam_date)
        goal = StudyGoal(
            user_id=user_id,
            title=request.title.strip(),
            description=request.description,
            exam_date=request.exam_date,
            target_score=request.target_score,
        )
        self.goals.add(goal)
        self.session.commit()
        return goal

    def list_goals(self, user_id: UUID) -> list[StudyGoal]:
        return [goal for goal in self.goals.list_by_user_id(user_id) if goal.status != "archived"]

    def get_goal(self, user_id: UUID, goal_id: UUID) -> StudyGoal:
        goal = self.goals.get_by_id(goal_id)
        if goal is None or goal.user_id != user_id or goal.status == "archived":
            raise GoalNotFoundError()
        return goal

    def update_goal(self, user_id: UUID, goal_id: UUID, request: GoalUpdateRequest) -> StudyGoal:
        self._validate_goal(request.title, request.exam_date)
        goal = self.get_goal(user_id, goal_id)
        goal.title = request.title.strip()
        goal.description = request.description
        goal.exam_date = request.exam_date
        goal.target_score = request.target_score
        self.session.commit()
        return goal

    def archive_goal(self, user_id: UUID, goal_id: UUID) -> None:
        goal = self.get_goal(user_id, goal_id)
        goal.status = "archived"
        self.session.commit()

    def create_subject(self, user_id: UUID, goal_id: UUID, request: SubjectCreateRequest) -> Subject:
        goal = self.get_goal(user_id, goal_id)
        ensure_non_empty(request.name, "Subject name")
        ensure_rating(request.priority, "priority")
        subject = Subject(
            goal_id=goal.id,
            user_id=user_id,
            name=request.name.strip(),
            description=request.description,
            priority=request.priority,
        )
        self.subjects.add(subject)
        self.session.commit()
        return subject

    def list_subjects(self, user_id: UUID, goal_id: UUID) -> list[Subject]:
        self.get_goal(user_id, goal_id)
        return [subject for subject in self.subjects.list_by_goal_id(goal_id) if subject.user_id == user_id]

    def create_topic(self, user_id: UUID, subject_id: UUID, request: TopicCreateRequest) -> Topic:
        subject = self._get_subject_for_user(user_id, subject_id)
        ensure_non_empty(request.name, "Topic name")
        ensure_rating(request.difficulty, "difficulty")
        ensure_rating(request.priority, "priority")
        ensure_positive_decimal(request.estimated_hours, "estimated_hours")
        topic = Topic(
            subject_id=subject.id,
            goal_id=subject.goal_id,
            user_id=user_id,
            name=request.name.strip(),
            description=request.description,
            difficulty=request.difficulty,
            priority=request.priority,
            estimated_hours=request.estimated_hours,
            is_manually_marked_weak=request.is_manually_marked_weak,
        )
        self.topics.add(topic)
        self.session.commit()
        return topic

    def list_topics(self, user_id: UUID, subject_id: UUID) -> list[Topic]:
        self._get_subject_for_user(user_id, subject_id)
        return [topic for topic in self.topics.list_by_subject_id(subject_id) if topic.user_id == user_id]

    def _get_subject_for_user(self, user_id: UUID, subject_id: UUID) -> Subject:
        subject = self.subjects.get_by_id(subject_id)
        if subject is None or subject.user_id != user_id:
            raise SubjectNotFoundError()
        self.get_goal(user_id, subject.goal_id)
        return subject

    @staticmethod
    def _validate_goal(title: str, exam_date) -> None:
        ensure_non_empty(title, "Goal title")
        ensure_exam_date_not_past(exam_date)

