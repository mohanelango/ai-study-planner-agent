import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.infrastructure.database.session import SessionLocal, check_database_connection
from app.main import app
from app.modules.users.repositories.postgres_repository import PostgresUserRepository


class AuthApiIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")
        self.client = TestClient(app)
        self.email = f"auth-{uuid4()}@example.com"
        self.password = "password123"

    def tearDown(self) -> None:
        if hasattr(self, "email"):
            with SessionLocal() as session:
                repo = PostgresUserRepository(session)
                user = repo.get_by_email(self.email)
                if user:
                    repo.delete(user)
                    session.commit()

    def register_user(self) -> dict:
        response = self.client.post("/api/v1/auth/register", json={"email": self.email, "password": self.password, "full_name": "Auth User"})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["data"]

    def test_register_login_and_me(self) -> None:
        data = self.register_user()
        self.assertEqual(data["email"], self.email)
        self.assertNotIn("password_hash", str(data))

        duplicate = self.client.post("/api/v1/auth/register", json={"email": self.email.upper(), "password": self.password})
        self.assertEqual(duplicate.status_code, 409)

        wrong = self.client.post("/api/v1/auth/login", json={"email": self.email, "password": "wrong-password"})
        self.assertEqual(wrong.status_code, 401)

        login = self.client.post("/api/v1/auth/login", json={"email": self.email, "password": self.password})
        self.assertEqual(login.status_code, 200, login.text)
        token = login.json()["data"]["access_token"]

        me = self.client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me.status_code, 200, me.text)
        self.assertEqual(me.json()["data"]["email"], self.email)
        self.assertNotIn("password_hash", str(me.json()))

    def test_protected_route_fails_without_token(self) -> None:
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()

