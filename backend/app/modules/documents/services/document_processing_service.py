from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.document_processing.pdf_extractor import PDFTextExtractor
from app.infrastructure.document_processing.text_chunker import TextChunker
from app.infrastructure.document_processing.text_cleaner import TextCleaner
from app.infrastructure.storage.base import StorageClient
from app.infrastructure.storage.factory import get_storage_client
from app.modules.documents.exceptions import DocumentNotFoundError
from app.modules.documents.infrastructure_models import DocumentChunk
from app.modules.documents.repositories.postgres_repository import PostgresDocumentChunkRepository, PostgresDocumentRepository
from app.modules.jobs.repositories.postgres_repository import PostgresBackgroundJobRepository


def sanitize_error(exc: Exception) -> str:
    return str(exc)[:500] or "Document processing failed"


class DocumentProcessingService:
    def __init__(self, session: Session, storage_client: StorageClient | None = None) -> None:
        self.session = session
        self.documents = PostgresDocumentRepository(session)
        self.chunks = PostgresDocumentChunkRepository(session)
        self.jobs = PostgresBackgroundJobRepository(session)
        self.storage = storage_client or get_storage_client()
        self.extractor = PDFTextExtractor()
        self.cleaner = TextCleaner()
        self.chunker = TextChunker()

    def process_document(self, document_id: UUID, background_job_id: UUID) -> dict:
        document = self.documents.get_by_id(document_id)
        if document is None or document.status == "deleted":
            raise DocumentNotFoundError()

        try:
            self.documents.update_status(document, "processing")
            self.jobs.update_status(background_job_id, "processing")
            self.session.commit()

            pdf_bytes = self.storage.download_file(document.storage_bucket, document.storage_key)
            pages = self.extractor.extract_pages(pdf_bytes)
            combined_text = "\n".join(page.text for page in pages)
            cleaned_text = self.cleaner.clean(combined_text)
            generated_chunks = self.chunker.chunk_pages(pages, cleaned_text)

            self.chunks.delete_by_document_id(document.id)
            chunk_rows = [
                DocumentChunk(
                    document_id=document.id,
                    user_id=document.user_id,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                    token_estimate=chunk.token_estimate,
                )
                for chunk in generated_chunks
            ]
            self.chunks.add_many(chunk_rows)
            self.documents.update_processing_result(document, len(cleaned_text), len(chunk_rows))
            result = {
                "document_id": str(document.id),
                "status": "processed",
                "chunk_count": len(chunk_rows),
                "extracted_text_char_count": len(cleaned_text),
            }
            self.jobs.update_status(background_job_id, "completed", result_payload=result)
            self.session.commit()
            return result
        except Exception as exc:
            self.session.rollback()
            message = sanitize_error(exc)
            document = self.documents.get_by_id(document_id)
            if document is not None:
                self.documents.update_status(document, "failed", message)
            self.jobs.update_status(background_job_id, "failed", error_message=message)
            self.session.commit()
            raise

