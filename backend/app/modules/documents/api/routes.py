from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.security.auth_dependencies import get_current_user
from app.infrastructure.database.session import get_db
from app.modules.documents.schemas.responses import BackgroundJobResponse
from app.modules.documents.services.document_service import DocumentService
from app.modules.users.infrastructure_models import User

router = APIRouter(tags=["documents"])


def success(message: str, data: object | None = None) -> dict:
    return {"success": True, "message": message, "data": data if data is not None else {}}


@router.post("/documents/upload")
def upload_document(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
    goal_id: UUID | None = Form(default=None),
    title: str | None = Form(default=None),
) -> dict:
    data = DocumentService(db).upload_document(current_user.id, file, goal_id, title)
    return success("Document uploaded successfully", data.model_dump(mode="json"))


@router.get("/documents")
def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    goal_id: UUID | None = Query(default=None),
) -> dict:
    data = [document.model_dump(mode="json") for document in DocumentService(db).list_documents(current_user.id, goal_id)]
    return success("Documents fetched successfully", data)


@router.get("/documents/{document_id}")
def get_document(document_id: UUID, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    data = DocumentService(db).get_document(current_user.id, document_id)
    return success("Document fetched successfully", data.model_dump(mode="json"))


@router.get("/documents/{document_id}/status")
def get_document_status(document_id: UUID, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    data = DocumentService(db).get_status(current_user.id, document_id)
    return success("Document status fetched successfully", data.model_dump(mode="json"))


@router.get("/documents/{document_id}/chunks")
def list_document_chunks(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    data = [chunk.model_dump(mode="json") for chunk in DocumentService(db).list_chunks(current_user.id, document_id, limit, offset)]
    return success("Document chunks fetched successfully", data)


@router.delete("/documents/{document_id}")
def delete_document(document_id: UUID, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    DocumentService(db).delete_document(current_user.id, document_id)
    return success("Document deleted successfully")


@router.get("/jobs/{job_id}")
def get_background_job(job_id: UUID, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    job = DocumentService(db).get_job(current_user.id, job_id)
    data = BackgroundJobResponse(
        id=job.id,
        job_type=job.job_type,
        entity_type=job.entity_type,
        entity_id=job.entity_id,
        status=job.status,
        result_payload=job.result_payload,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
    )
    return success("Background job fetched successfully", data.model_dump(mode="json"))

