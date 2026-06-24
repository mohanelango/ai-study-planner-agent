from datetime import date, timedelta
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.main import app
from app.modules.users.repositories.postgres_repository import PostgresUserRepository


class GoalApiIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")
        self.client = TestClient(app)
        self.email = f"goal-api-{uuid4()}@example.com"
        self.other_email = f"other-goal-api-{uuid4()}@example.com"
        self.password = "password123"
        self.headers = self._register_and_login(self.email)
        self.other_headers = self._register_and_login(self.other_email)

    def tearDown(self) -> None:
        for email in (getattr(self, "email", None), getattr(self, "other_email", None)):
            if email:
                with SessionLocal() as session:
                    repo = PostgresUserRepository(session)
                    user = repo.get_by_email(email)
                    if user:
                        repo.delete(user)
                        session.commit()

    def _register_and_login(self, email: str) -> dict[str, str]:
        self.client.post("/api/v1/auth/register", json={"email": email, "password": self.password})
        login = self.client.post("/api/v1/auth/login", json={"email": email, "password": self.password})
        token = login.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_goal_subject_topic_flow_and_ownership(self) -> None:
        exam_date = (date.today() + timedelta(days=30)).isoformat()
        create_goal = self.client.post(
            "/api/v1/goals",
            json={"title": "Prepare for exam", "description": None, "exam_date": exam_date, "target_score": "90%"},
            headers=self.headers,
        )
        self.assertEqual(create_goal.status_code, 200, create_goal.text)
        goal_id = create_goal.json()["data"]["id"]
        self.assertNotIn("email", str(create_goal.json()["data"]))

        other_access = self.client.get(f"/api/v1/goals/{goal_id}", headers=self.other_headers)
        self.assertEqual(other_access.status_code, 404)

        listed = self.client.get("/api/v1/goals", headers=self.headers)
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(len(listed.json()["data"]), 1)

        detail = self.client.get(f"/api/v1/goals/{goal_id}", headers=self.headers)
        self.assertEqual(detail.status_code, 200, detail.text)

        updated = self.client.put(
            f"/api/v1/goals/{goal_id}",
            json={"title": "Updated exam", "description": "Focus", "exam_date": exam_date, "target_score": "95%"},
            headers=self.headers,
        )
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(updated.json()["data"]["title"], "Updated exam")

        subject = self.client.post(
            f"/api/v1/goals/{goal_id}/subjects",
            json={"name": "Mathematics", "description": None, "priority": 3},
            headers=self.headers,
        )
        self.assertEqual(subject.status_code, 200, subject.text)
        subject_id = subject.json()["data"]["id"]

        subjects = self.client.get(f"/api/v1/goals/{goal_id}/subjects", headers=self.headers)
        self.assertEqual(subjects.status_code, 200, subjects.text)
        self.assertEqual(len(subjects.json()["data"]), 1)

        topic = self.client.post(
            f"/api/v1/subjects/{subject_id}/topics",
            json={"name": "Algebra", "description": None, "difficulty": 3, "priority": 3, "estimated_hours": 2.5, "is_manually_marked_weak": False},
            headers=self.headers,
        )
        self.assertEqual(topic.status_code, 200, topic.text)

        topics = self.client.get(f"/api/v1/subjects/{subject_id}/topics", headers=self.headers)
        self.assertEqual(topics.status_code, 200, topics.text)
        self.assertEqual(len(topics.json()["data"]), 1)

        archived = self.client.delete(f"/api/v1/goals/{goal_id}", headers=self.headers)
        self.assertEqual(archived.status_code, 200, archived.text)
        gone = self.client.get(f"/api/v1/goals/{goal_id}", headers=self.headers)
        self.assertEqual(gone.status_code, 404)


if __name__ == "__main__":
    unittest.main()

