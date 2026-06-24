from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.goals.infrastructure_models import StudyGoal, Subject, Topic
from app.modules.goals.repositories.interfaces import StudyGoalRepository, SubjectRepository, TopicRepository


class PostgresStudyGoalRepository(StudyGoalRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: StudyGoal) -> StudyGoal:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> StudyGoal | None:
        return self.session.get(StudyGoal, entity_id)

    def list_by_user_id(self, user_id: UUID) -> list[StudyGoal]:
        return list(self.session.scalars(select(StudyGoal).where(StudyGoal.user_id == user_id)))

    def delete(self, entity: StudyGoal) -> None:
        self.session.delete(entity)


class PostgresSubjectRepository(SubjectRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: Subject) -> Subject:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> Subject | None:
        return self.session.get(Subject, entity_id)

    def list_by_user_id(self, user_id: UUID) -> list[Subject]:
        return list(self.session.scalars(select(Subject).where(Subject.user_id == user_id)))

    def list_by_goal_id(self, goal_id: UUID) -> list[Subject]:
        return list(self.session.scalars(select(Subject).where(Subject.goal_id == goal_id)))

    def delete(self, entity: Subject) -> None:
        self.session.delete(entity)


class PostgresTopicRepository(TopicRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: Topic) -> Topic:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> Topic | None:
        return self.session.get(Topic, entity_id)

    def list_by_user_id(self, user_id: UUID) -> list[Topic]:
        return list(self.session.scalars(select(Topic).where(Topic.user_id == user_id)))

    def list_by_goal_id(self, goal_id: UUID) -> list[Topic]:
        return list(self.session.scalars(select(Topic).where(Topic.goal_id == goal_id)))

    def list_by_subject_id(self, subject_id: UUID) -> list[Topic]:
        return list(self.session.scalars(select(Topic).where(Topic.subject_id == subject_id)))

    def delete(self, entity: Topic) -> None:
        self.session.delete(entity)

