import unittest
from uuid import uuid4

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.modules.jobs.infrastructure_models import BackgroundJob
from app.modules.jobs.repositories.postgres_repository import PostgresBackgroundJobRepository
from app.modules.users.infrastructure_models import User
from app.modules.users.repositories.postgres_repository import PostgresUserRepository


class BackgroundJobRepositoryTestCase(unittest.TestCase):
    def require_database(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")

    def test_background_job_repository_can_create_and_update_status(self) -> None:
        self.require_database()

        with SessionLocal() as session:
            user_repo = PostgresUserRepository(session)
            job_repo = PostgresBackgroundJobRepository(session)

            user = user_repo.add(User(email=f"jobs-{uuid4()}@example.com", password_hash="hashed-password"))
            job = job_repo.add(
                BackgroundJob(
                    user_id=user.id,
                    job_type="health_check",
                    entity_type="test",
                    input_payload={"source": "integration_test"},
                )
            )
            session.commit()

            self.assertIsNotNone(job_repo.get_by_id(job.id))
            self.assertEqual(len(job_repo.list_by_user_id(user.id)), 1)

            updated = job_repo.update_status(job.id, "completed")
            session.commit()

            self.assertIsNotNone(updated)
            self.assertEqual(updated.status, "completed")

            user_repo.delete(user)
            session.commit()


if __name__ == "__main__":
    unittest.main()
