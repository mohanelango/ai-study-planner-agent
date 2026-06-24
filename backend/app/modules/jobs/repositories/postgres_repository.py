from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.jobs.infrastructure_models import BackgroundJob
from app.modules.jobs.repositories.interfaces import BackgroundJobRepository


class PostgresBackgroundJobRepository(BackgroundJobRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: BackgroundJob) -> BackgroundJob:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> BackgroundJob | None:
        return self.session.get(BackgroundJob, entity_id)

    def update_status(
        self,
        job_id: UUID,
        status: str,
        error_message: str | None = None,
        result_payload: dict | None = None,
    ) -> BackgroundJob | None:
        job = self.get_by_id(job_id)
        if job is None:
            return None
        job.status = status
        job.error_message = error_message
        if result_payload is not None:
            job.result_payload = result_payload
        if status == "processing" and job.started_at is None:
            job.started_at = datetime.now(timezone.utc)
        if status in {"completed", "failed"}:
            job.completed_at = datetime.now(timezone.utc)
        self.session.flush()
        return job

    def list_by_user_id(self, user_id: UUID) -> list[BackgroundJob]:
        return list(self.session.scalars(select(BackgroundJob).where(BackgroundJob.user_id == user_id)))

    def delete(self, entity: BackgroundJob) -> None:
        self.session.delete(entity)
