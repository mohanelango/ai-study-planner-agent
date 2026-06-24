from datetime import date
from decimal import Decimal
import unittest
from uuid import uuid4

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.modules.goals.infrastructure_models import StudyGoal, Subject, Topic
from app.modules.goals.repositories.postgres_repository import (
    PostgresStudyGoalRepository,
    PostgresSubjectRepository,
    PostgresTopicRepository,
)
from app.modules.users.infrastructure_models import User
from app.modules.users.repositories.postgres_repository import PostgresUserRepository


class GoalRepositoryTestCase(unittest.TestCase):
    def require_database(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")

    def test_goal_subject_and_topic_repositories(self) -> None:
        self.require_database()

        with SessionLocal() as session:
            user_repo = PostgresUserRepository(session)
            goal_repo = PostgresStudyGoalRepository(session)
            subject_repo = PostgresSubjectRepository(session)
            topic_repo = PostgresTopicRepository(session)

            user = user_repo.add(User(email=f"goals-{uuid4()}@example.com", password_hash="hashed-password"))
            goal = goal_repo.add(
                StudyGoal(
                    user_id=user.id,
                    title="Prepare for exam",
                    exam_date=date(2026, 12, 31),
                )
            )
            subject = subject_repo.add(Subject(goal_id=goal.id, user_id=user.id, name="Mathematics"))
            topic = topic_repo.add(
                Topic(
                    subject_id=subject.id,
                    goal_id=goal.id,
                    user_id=user.id,
                    name="Algebra",
                    estimated_hours=Decimal("2.50"),
                )
            )
            session.commit()

            self.assertIsNotNone(goal_repo.get_by_id(goal.id))
            self.assertEqual(len(goal_repo.list_by_user_id(user.id)), 1)
            self.assertEqual(len(subject_repo.list_by_goal_id(goal.id)), 1)
            self.assertEqual(len(topic_repo.list_by_subject_id(subject.id)), 1)
            self.assertEqual(len(topic_repo.list_by_goal_id(goal.id)), 1)
            self.assertIsNotNone(topic_repo.get_by_id(topic.id))

            user_repo.delete(user)
            session.commit()


if __name__ == "__main__":
    unittest.main()
