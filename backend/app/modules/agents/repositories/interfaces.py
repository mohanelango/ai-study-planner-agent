from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.agents.infrastructure_models import AgentRun, LLMPrompt, LLMResponse
from app.shared.base.base_repository import BaseRepository


class AgentRunRepository(BaseRepository[AgentRun], ABC):
    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[AgentRun]: ...

    @abstractmethod
    def update_status(self, agent_run: AgentRun, status: str, error_message: str | None = None, output_summary: str | None = None) -> AgentRun: ...


class LLMPromptRepository(BaseRepository[LLMPrompt], ABC):
    pass


class LLMResponseRepository(BaseRepository[LLMResponse], ABC):
    @abstractmethod
    def attach_response(self, response: LLMResponse) -> LLMResponse: ...

