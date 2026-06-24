import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.main import app
from app.modules.users.repositories.postgres_repository import PostgresUserRepository


class ProfileApiIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")
        self.client = TestClient(app)
        self.email = f"profile-api-{uuid4()}@example.com"
        self.password = "password123"
        self.client.post("/api/v1/auth/register", json={"email": self.email, "password": self.password})
        login = self.client.post("/api/v1/auth/login", json={"email": self.email, "password": self.password})
        self.token = login.json()["data"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self) -> None:
        if hasattr(self, "email"):
            with SessionLocal() as session:
                repo = PostgresUserRepository(session)
                user = repo.get_by_email(self.email)
                if user:
                    repo.delete(user)
                    session.commit()

    def test_profile_create_get_update_and_availability(self) -> None:
        profile_payload = {
            "education_level": "Undergraduate",
            "timezone": "Asia/Kolkata",
            "preferred_study_duration_minutes": 45,
            "learning_style": "visual",
            "daily_goal_minutes": 90,
        }
        create_profile = self.client.post("/api/v1/profiles", json=profile_payload, headers=self.headers)
        self.assertEqual(create_profile.status_code, 200, create_profile.text)
        self.assertNotIn("password_hash", str(create_profile.json()))

        get_profile = self.client.get("/api/v1/profiles/me", headers=self.headers)
        self.assertEqual(get_profile.status_code, 200, get_profile.text)
        self.assertEqual(get_profile.json()["data"]["education_level"], "Undergraduate")

        update_profile = self.client.put(
            "/api/v1/profiles/me",
            json={**profile_payload, "daily_goal_minutes": 120},
            headers=self.headers,
        )
        self.assertEqual(update_profile.status_code, 200, update_profile.text)
        self.assertEqual(update_profile.json()["data"]["daily_goal_minutes"], 120)

        availability = self.client.post(
            "/api/v1/availability",
            json={"day_of_week": 1, "start_time": "09:00", "end_time": "10:00"},
            headers=self.headers,
        )
        self.assertEqual(availability.status_code, 200, availability.text)
        availability_id = availability.json()["data"]["id"]

        listing = self.client.get("/api/v1/availability", headers=self.headers)
        self.assertEqual(listing.status_code, 200, listing.text)
        self.assertEqual(len(listing.json()["data"]), 1)

        deleted = self.client.delete(f"/api/v1/availability/{availability_id}", headers=self.headers)
        self.assertEqual(deleted.status_code, 200, deleted.text)


if __name__ == "__main__":
    unittest.main()

