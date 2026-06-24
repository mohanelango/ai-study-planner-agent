from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.documents.infrastructure_models import Document, DocumentChunk
from app.shared.base.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document], ABC):
    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def list_by_goal_id(self, user_id: UUID, goal_id: UUID) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, document: Document, status: str, processing_error: str | None = None) -> Document:
        raise NotImplementedError

    @abstractmethod
    def update_processing_result(self, document: Document, extracted_text_char_count: int, chunk_count: int) -> Document:
        raise NotImplementedError

    @abstractmethod
    def mark_deleted(self, document: Document) -> Document:
        raise NotImplementedError


class DocumentChunkRepository(ABC):
    @abstractmethod
    def add_many(self, entities: list[DocumentChunk]) -> list[DocumentChunk]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_document_id(self, document_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_document_id(self, document_id: UUID, limit: int = 50, offset: int = 0) -> list[DocumentChunk]:
        raise NotImplementedError

    @abstractmethod
    def count_by_document_id(self, document_id: UUID) -> int:
        raise NotImplementedError

