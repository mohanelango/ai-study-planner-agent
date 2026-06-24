import unittest

from sqlalchemy import text

from app.infrastructure.database.session import SessionLocal, check_database_connection


class DatabaseConnectionTestCase(unittest.TestCase):
    def test_database_connection_can_execute_select_one(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")

        with SessionLocal() as session:
            result = session.execute(text("SELECT 1")).scalar_one()

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
