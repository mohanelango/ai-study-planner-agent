from uuid import UUID

from app.infrastructure.database.session import SessionLocal
from app.modules.documents.services.document_processing_service import DocumentProcessingService
from app.worker import celery_app


@celery_app.task(name="documents.process_uploaded_document", queue="documents", autoretry_for=(), max_retries=0)
def process_uploaded_document(document_id: str, background_job_id: str) -> dict:
    with SessionLocal() as session:
        return DocumentProcessingService(session).process_document(UUID(document_id), UUID(background_job_id))

