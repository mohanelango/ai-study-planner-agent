from datetime import datetime, timezone
import unittest
from uuid import uuid4

from app.core.security.password_hasher import hash_password, verify_password
from app.modules.users.domain.rules import normalize_email
from app.modules.users.infrastructure_models import User


class AuthServiceUnitTestCase(unittest.TestCase):
    def test_password_hash_verification(self) -> None:
        password_hash = hash_password("password123")
        self.assertNotEqual(password_hash, "password123")
        self.assertTrue(verify_password("password123", password_hash))
        self.assertFalse(verify_password("wrong-password", password_hash))

    def test_email_normalization_and_safe_repr(self) -> None:
        self.assertEqual(normalize_email(" USER@Example.COM "), "user@example.com")
        user = User(id=uuid4(), email="user@example.com", password_hash="secret-hash", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        self.assertNotIn("secret-hash", repr(user))


if __name__ == "__main__":
    unittest.main()

