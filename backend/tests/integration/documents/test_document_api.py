import unittest
from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient

from app.infrastructure.database.session import check_database_connection
from app.main import app


class DocumentApiIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not check_database_connection():
            self.skipTest("PostgreSQL is not available. Start Docker Compose and run Alembic migrations first.")
        self.client = TestClient(app)

    def test_upload_requires_auth(self) -> None:
        response = self.client.post("/api/v1/documents/upload", files={"file": ("notes.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")})
        self.assertEqual(response.status_code, 401)

    def test_document_detail_requires_auth_and_does_not_expose_storage_fields(self) -> None:
        response = self.client.get(f"/api/v1/documents/{uuid4()}")
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("storage_bucket", response.text)
        self.assertNotIn("storage_key", response.text)


if __name__ == "__main__":
    unittest.main()

