from datetime import date, timedelta
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.infrastructure.llm.base import LLMProvider, LLMRequest, LLMResponse
from app.main import app
from app.modules.agents.infrastructure_models import AgentRun
from app.modules.planning.infrastructure_models import StudySession, StudyTask
from app.modules.users.repositories.postgres_repository import PostgresUserRepository


class MockLLMProvider(LLMProvider):
    def __init__(self, parsed_json: dict | None = None) -> None:
        self.parsed_json = parsed_json or {
            "headline": "Your plan is ready",
            "summary": "This explains the deterministic plan.",
            "priority_rationale": ["Higher priority topics appear earlier."],
            "schedule_rationale": ["Sessions follow available windows."],
            "risk_warnings": [],
            "next_best_actions": ["Start with the first task."],
        }

    def generate_json(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content='{"safe": true}', parsed_json=self.parsed_json, model="mock", provider="mock", total_tokens=10)

    def generate_text(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content="text", parsed_json=None, model="mock", provider="mock")


class PlanExplanationApiIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")
        self.client = TestClient(app)
        self.password = "password123"
        self.email = f"agent-{uuid4()}@example.com"
        self.headers = self._register_and_login(self.email)

    def tearDown(self) -> None:
        if hasattr(self, "email"):
            with SessionLocal() as session:
                repo = PostgresUserRepository(session)
                user = repo.get_by_email(self.email)
                if user:
                    repo.delete(user)
                    session.commit()

    def _register_and_login(self, email: str) -> dict[str, str]:
        self.client.post("/api/v1/auth/register", json={"email": email, "password": self.password})
        login = self.client.post("/api/v1/auth/login", json={"email": email, "password": self.password})
        return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    def _create_plan(self) -> str:
        self.client.post("/api/v1/profiles", json={"education_level": "UG", "timezone": "Asia/Kolkata", "preferred_study_duration_minutes": 60, "learning_style": None, "daily_goal_minutes": 120}, headers=self.headers)
        self.client.post("/api/v1/availability", json={"day_of_week": date.today().weekday(), "start_time": "09:00", "end_time": "11:00"}, headers=self.headers)
        goal = self.client.post("/api/v1/goals", json={"title": "Agent Exam", "description": None, "exam_date": (date.today() + timedelta(days=21)).isoformat(), "target_score": "90"}, headers=self.headers)
        goal_id = goal.json()["data"]["id"]
        subject = self.client.post(f"/api/v1/goals/{goal_id}/subjects", json={"name": "Math", "description": None, "priority": 5}, headers=self.headers)
        subject_id = subject.json()["data"]["id"]
        self.client.post(f"/api/v1/subjects/{subject_id}/topics", json={"name": "Algebra", "description": None, "difficulty": 5, "priority": 5, "estimated_hours": 2, "is_manually_marked_weak": False}, headers=self.headers)
        plan = self.client.post("/api/v1/plans/generate", json={"goal_id": goal_id, "preferred_session_minutes": 60, "include_revision_sessions": True}, headers=self.headers)
        return plan.json()["data"]["study_plan_id"]

    def test_explain_requires_auth(self) -> None:
        response = self.client.post(f"/api/v1/plans/{uuid4()}/explain")
        self.assertEqual(response.status_code, 401)

    def test_explanation_logs_agent_run_and_hides_raw_data(self) -> None:
        plan_id = self._create_plan()
        with SessionLocal() as session:
            before_sessions = session.query(StudySession).count()
            before_tasks = session.query(StudyTask).count()

        with patch("app.modules.agents.services.study_plan_explanation_service.get_llm_provider", return_value=MockLLMProvider()):
            response = self.client.post(f"/api/v1/plans/{plan_id}/explain", headers=self.headers)

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()["data"]
        self.assertIn("headline", body)
        self.assertNotIn("raw_response", str(body))
        self.assertNotIn("user_prompt", str(body))
        self.assertNotIn("total_tokens", str(body))

        with SessionLocal() as session:
            after_sessions = session.query(StudySession).count()
            after_tasks = session.query(StudyTask).count()
            self.assertEqual(before_sessions, after_sessions)
            self.assertEqual(before_tasks, after_tasks)
            self.assertGreater(session.query(AgentRun).count(), 0)


if __name__ == "__main__":
    unittest.main()

