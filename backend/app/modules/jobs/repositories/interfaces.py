from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.jobs.infrastructure_models import BackgroundJob
from app.shared.base.base_repository import BaseRepository


class BackgroundJobRepository(BaseRepository[BackgroundJob], ABC):
    @abstractmethod
    def update_status(
        self,
        job_id: UUID,
        status: str,
        error_message: str | None = None,
        result_payload: dict | None = None,
    ) -> BackgroundJob | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[BackgroundJob]:
        raise NotImplementedError
