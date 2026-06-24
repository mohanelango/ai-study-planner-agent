from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.documents.infrastructure_models import Document, DocumentChunk
from app.modules.documents.repositories.interfaces import DocumentChunkRepository, DocumentRepository


class PostgresDocumentRepository(DocumentRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: Document) -> Document:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> Document | None:
        return self.session.get(Document, entity_id)

    def list_by_user_id(self, user_id: UUID) -> list[Document]:
        return list(self.session.scalars(select(Document).where(Document.user_id == user_id, Document.status != "deleted").order_by(Document.created_at.desc())))

    def list_by_goal_id(self, user_id: UUID, goal_id: UUID) -> list[Document]:
        return list(self.session.scalars(select(Document).where(Document.user_id == user_id, Document.goal_id == goal_id, Document.status != "deleted").order_by(Document.created_at.desc())))

    def update_status(self, document: Document, status: str, processing_error: str | None = None) -> Document:
        document.status = status
        document.processing_error = processing_error
        self.session.flush()
        return document

    def update_processing_result(self, document: Document, extracted_text_char_count: int, chunk_count: int) -> Document:
        document.status = "processed"
        document.processing_error = None
        document.extracted_text_char_count = extracted_text_char_count
        document.chunk_count = chunk_count
        document.processed_at = datetime.now(timezone.utc)
        self.session.flush()
        return document

    def mark_deleted(self, document: Document) -> Document:
        document.status = "deleted"
        self.session.flush()
        return document

    def delete(self, entity: Document) -> None:
        self.session.delete(entity)


class PostgresDocumentChunkRepository(DocumentChunkRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_many(self, entities: list[DocumentChunk]) -> list[DocumentChunk]:
        self.session.add_all(entities)
        self.session.flush()
        return entities

    def delete_by_document_id(self, document_id: UUID) -> None:
        self.session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
        self.session.flush()

    def list_by_document_id(self, document_id: UUID, limit: int = 50, offset: int = 0) -> list[DocumentChunk]:
        query = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index).limit(limit).offset(offset)
        return list(self.session.scalars(query))

    def count_by_document_id(self, document_id: UUID) -> int:
        return int(self.session.scalar(select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == document_id)) or 0)

