from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal_id: UUID | None
    title: str
    original_filename: str
    content_type: str
    file_size_bytes: int | None
    status: str
    extracted_text_char_count: int | None
    chunk_count: int | None
    uploaded_at: datetime | None
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    background_job_id: UUID


class DocumentStatusResponse(BaseModel):
    id: UUID
    title: str
    original_filename: str
    status: str
    extracted_text_char_count: int | None
    chunk_count: int | None
    uploaded_at: datetime | None
    processed_at: datetime | None
    processing_error: str | None = None


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    chunk_index: int
    text: str
    page_start: int | None
    page_end: int | None
    token_estimate: int | None


class BackgroundJobResponse(BaseModel):
    id: UUID
    job_type: str
    entity_type: str | None
    entity_id: UUID | None
    status: str
    result_payload: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

