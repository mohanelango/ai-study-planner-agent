from datetime import date, timedelta
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.main import app
from app.modules.users.repositories.postgres_repository import PostgresUserRepository


class PlanningApiIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")
        self.client = TestClient(app)
        self.password = "password123"
        self.email = f"planner-{uuid4()}@example.com"
        self.other_email = f"planner-other-{uuid4()}@example.com"
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
        return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    def _seed_goal_subject_topic_availability(self) -> str:
        self.client.post(
            "/api/v1/profiles",
            json={"education_level": "UG", "timezone": "Asia/Kolkata", "preferred_study_duration_minutes": 60, "learning_style": None, "daily_goal_minutes": 120},
            headers=self.headers,
        )
        self.client.post(
            "/api/v1/availability",
            json={"day_of_week": date.today().weekday(), "start_time": "09:00", "end_time": "11:00"},
            headers=self.headers,
        )
        goal = self.client.post(
            "/api/v1/goals",
            json={"title": "Planner Exam", "description": None, "exam_date": (date.today() + timedelta(days=21)).isoformat(), "target_score": "90"},
            headers=self.headers,
        )
        goal_id = goal.json()["data"]["id"]
        subject = self.client.post(
            f"/api/v1/goals/{goal_id}/subjects",
            json={"name": "Math", "description": None, "priority": 5},
            headers=self.headers,
        )
        subject_id = subject.json()["data"]["id"]
        self.client.post(
            f"/api/v1/subjects/{subject_id}/topics",
            json={"name": "Algebra", "description": None, "difficulty": 5, "priority": 5, "estimated_hours": 2, "is_manually_marked_weak": False},
            headers=self.headers,
        )
        return goal_id

    def test_generate_calendar_today_duplicate_and_ownership(self) -> None:
        goal_id = self._seed_goal_subject_topic_availability()
        generated = self.client.post(
            "/api/v1/plans/generate",
            json={"goal_id": goal_id, "plan_title": "Rule Plan", "include_revision_sessions": True, "preferred_session_minutes": 60},
            headers=self.headers,
        )
        self.assertEqual(generated.status_code, 200, generated.text)
        plan_id = generated.json()["data"]["study_plan_id"]
        self.assertGreater(generated.json()["data"]["total_sessions"], 0)
        self.assertGreater(generated.json()["data"]["total_tasks"], 0)

        duplicate = self.client.post(
            "/api/v1/plans/generate",
            json={"goal_id": goal_id, "preferred_session_minutes": 60, "include_revision_sessions": True},
            headers=self.headers,
        )
        self.assertEqual(duplicate.status_code, 409)

        calendar = self.client.get(f"/api/v1/plans/{plan_id}/calendar", headers=self.headers)
        self.assertEqual(calendar.status_code, 200, calendar.text)
        self.assertGreater(len(calendar.json()["data"]["sessions"]), 0)
        self.assertGreater(len(calendar.json()["data"]["sessions"][0]["tasks"]), 0)

        today = self.client.get(f"/api/v1/plans/{plan_id}/today", headers=self.headers)
        self.assertEqual(today.status_code, 200, today.text)
        self.assertIn("sessions", today.json()["data"])

        versions = self.client.get(f"/api/v1/plans/{plan_id}/versions", headers=self.headers)
        self.assertEqual(versions.status_code, 200, versions.text)
        self.assertEqual(versions.json()["data"][0]["version_number"], 1)

        other_calendar = self.client.get(f"/api/v1/plans/{plan_id}/calendar", headers=self.other_headers)
        self.assertEqual(other_calendar.status_code, 404)


if __name__ == "__main__":
    unittest.main()

