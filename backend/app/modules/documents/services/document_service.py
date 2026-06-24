import re
from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.infrastructure.storage.base import StorageClient
from app.infrastructure.storage.factory import get_storage_client
from app.modules.documents.exceptions import BackgroundJobNotFoundError, DocumentNotFoundError, InvalidDocumentUploadError
from app.modules.documents.infrastructure_models import Document
from app.modules.documents.repositories.postgres_repository import PostgresDocumentChunkRepository, PostgresDocumentRepository
from app.modules.documents.schemas.responses import DocumentChunkResponse, DocumentResponse, DocumentStatusResponse, DocumentUploadResponse
from app.modules.goals.exceptions import GoalNotFoundError
from app.modules.goals.repositories.postgres_repository import PostgresStudyGoalRepository
from app.modules.jobs.infrastructure_models import BackgroundJob
from app.modules.jobs.repositories.postgres_repository import PostgresBackgroundJobRepository

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


def safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", filename.strip())
    return cleaned or "document.pdf"


class DocumentService:
    def __init__(self, session: Session, storage_client: StorageClient | None = None) -> None:
        self.session = session
        self.documents = PostgresDocumentRepository(session)
        self.chunks = PostgresDocumentChunkRepository(session)
        self.goals = PostgresStudyGoalRepository(session)
        self.jobs = PostgresBackgroundJobRepository(session)
        self.storage = storage_client or get_storage_client()

    def upload_document(self, user_id: UUID, file: UploadFile, goal_id: UUID | None = None, title: str | None = None) -> DocumentUploadResponse:
        self._validate_goal(user_id, goal_id)
        filename = file.filename or "document.pdf"
        content_type = file.content_type or "application/octet-stream"
        if content_type not in PDF_CONTENT_TYPES and not filename.lower().endswith(".pdf"):
            raise InvalidDocumentUploadError("Only PDF uploads are supported", "UNSUPPORTED_FILE_TYPE")

        content = file.file.read()
        if not content:
            raise InvalidDocumentUploadError("Uploaded file is empty", "EMPTY_UPLOAD")
        if len(content) > MAX_UPLOAD_BYTES:
            raise InvalidDocumentUploadError("PDF file size must be 10 MB or less", "FILE_TOO_LARGE")

        document = Document(
            user_id=user_id,
            goal_id=goal_id,
            title=(title.strip() if title else filename.rsplit(".", 1)[0]),
            original_filename=filename,
            content_type="application/pdf",
            file_size_bytes=len(content),
            storage_bucket=settings.MINIO_BUCKET,
            storage_key="pending",
            status="uploaded",
            uploaded_at=datetime.now(timezone.utc),
        )
        try:
            self.documents.add(document)
            document.storage_key = f"users/{user_id}/documents/{document.id}/{safe_filename(filename)}"
            self.storage.upload_file(document.storage_bucket, document.storage_key, BytesIO(content), len(content), "application/pdf")
            job = self.jobs.add(
                BackgroundJob(
                    user_id=user_id,
                    job_type="document_processing",
                    entity_type="document",
                    entity_id=document.id,
                    status="queued",
                    input_payload={"document_id": str(document.id)},
                )
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        from app.modules.documents.tasks.process_document import process_uploaded_document

        task = process_uploaded_document.apply_async(args=[str(document.id), str(job.id)], queue="documents")
        job.celery_task_id = task.id
        self.session.commit()
        return DocumentUploadResponse(document=DocumentResponse.model_validate(document), background_job_id=job.id)

    def list_documents(self, user_id: UUID, goal_id: UUID | None = None) -> list[DocumentResponse]:
        rows = self.documents.list_by_goal_id(user_id, goal_id) if goal_id else self.documents.list_by_user_id(user_id)
        return [DocumentResponse.model_validate(row) for row in rows]

    def get_document(self, user_id: UUID, document_id: UUID) -> DocumentResponse:
        return DocumentResponse.model_validate(self._get_document_for_user(user_id, document_id))

    def get_status(self, user_id: UUID, document_id: UUID) -> DocumentStatusResponse:
        document = self._get_document_for_user(user_id, document_id)
        return DocumentStatusResponse(
            id=document.id,
            title=document.title,
            original_filename=document.original_filename,
            status=document.status,
            extracted_text_char_count=document.extracted_text_char_count,
            chunk_count=document.chunk_count,
            uploaded_at=document.uploaded_at,
            processed_at=document.processed_at,
            processing_error=document.processing_error if document.status == "failed" else None,
        )

    def list_chunks(self, user_id: UUID, document_id: UUID, limit: int = 50, offset: int = 0) -> list[DocumentChunkResponse]:
        self._get_document_for_user(user_id, document_id)
        rows = self.chunks.list_by_document_id(document_id, limit=min(limit, 100), offset=max(offset, 0))
        return [DocumentChunkResponse.model_validate(row) for row in rows]

    def delete_document(self, user_id: UUID, document_id: UUID) -> None:
        document = self._get_document_for_user(user_id, document_id)
        self.documents.mark_deleted(document)
        try:
            self.storage.delete_file(document.storage_bucket, document.storage_key)
        except Exception:
            pass
        self.session.commit()

    def get_job(self, user_id: UUID, job_id: UUID):
        job = self.jobs.get_by_id(job_id)
        if job is None or job.user_id != user_id:
            raise BackgroundJobNotFoundError()
        return job

    def _get_document_for_user(self, user_id: UUID, document_id: UUID) -> Document:
        document = self.documents.get_by_id(document_id)
        if document is None or document.user_id != user_id or document.status == "deleted":
            raise DocumentNotFoundError()
        return document

    def _validate_goal(self, user_id: UUID, goal_id: UUID | None) -> None:
        if goal_id is None:
            return
        goal = self.goals.get_by_id(goal_id)
        if goal is None or goal.user_id != user_id or goal.status == "archived":
            raise GoalNotFoundError()

