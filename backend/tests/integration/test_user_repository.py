from datetime import time
import unittest
from uuid import uuid4

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.modules.users.infrastructure_models import AvailabilityWindow, StudentProfile, User
from app.modules.users.repositories.postgres_repository import (
    PostgresAvailabilityWindowRepository,
    PostgresStudentProfileRepository,
    PostgresUserRepository,
)


class UserRepositoryTestCase(unittest.TestCase):
    def require_database(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")

    def test_user_repository_can_create_and_fetch_user_by_id_and_email(self) -> None:
        self.require_database()
        email = f"weekend2-{uuid4()}@example.com"

        with SessionLocal() as session:
            repo = PostgresUserRepository(session)
            user = repo.add(User(email=email, password_hash="hashed-password", full_name="Weekend Two"))
            session.commit()

            self.assertIsNotNone(repo.get_by_id(user.id))
            self.assertIsNotNone(repo.get_by_email(email))
            self.assertNotIn("hashed-password", repr(user))

            repo.delete(user)
            session.commit()

    def test_profile_and_availability_repositories_can_list_by_user(self) -> None:
        self.require_database()

        with SessionLocal() as session:
            user_repo = PostgresUserRepository(session)
            profile_repo = PostgresStudentProfileRepository(session)
            availability_repo = PostgresAvailabilityWindowRepository(session)

            user = user_repo.add(User(email=f"profile-{uuid4()}@example.com", password_hash="hashed-password"))
            profile_repo.add(StudentProfile(user_id=user.id))
            availability_repo.add(
                AvailabilityWindow(
                    user_id=user.id,
                    day_of_week=1,
                    start_time=time(9, 0),
                    end_time=time(10, 0),
                )
            )
            session.commit()

            self.assertIsNotNone(profile_repo.get_by_user_id(user.id))
            self.assertEqual(len(availability_repo.list_by_user_id(user.id)), 1)

            user_repo.delete(user)
            session.commit()


if __name__ == "__main__":
    unittest.main()
