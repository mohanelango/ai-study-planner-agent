from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.agents.infrastructure_models import AgentRun, LLMPrompt, LLMResponse
from app.modules.agents.repositories.interfaces import AgentRunRepository, LLMPromptRepository, LLMResponseRepository


class PostgresAgentRunRepository(AgentRunRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: AgentRun) -> AgentRun:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> AgentRun | None:
        return self.session.get(AgentRun, entity_id)

    def list_by_user_id(self, user_id: UUID) -> list[AgentRun]:
        return list(self.session.scalars(select(AgentRun).where(AgentRun.user_id == user_id)))

    def update_status(self, agent_run: AgentRun, status: str, error_message: str | None = None, output_summary: str | None = None) -> AgentRun:
        agent_run.status = status
        agent_run.error_message = error_message
        if output_summary is not None:
            agent_run.output_summary = output_summary
        if status in {"completed", "failed"}:
            agent_run.completed_at = datetime.now(timezone.utc)
        self.session.flush()
        return agent_run

    def delete(self, entity: AgentRun) -> None:
        self.session.delete(entity)


class PostgresLLMPromptRepository(LLMPromptRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: LLMPrompt) -> LLMPrompt:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> LLMPrompt | None:
        return self.session.get(LLMPrompt, entity_id)

    def delete(self, entity: LLMPrompt) -> None:
        self.session.delete(entity)


class PostgresLLMResponseRepository(LLMResponseRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, entity: LLMResponse) -> LLMResponse:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: UUID) -> LLMResponse | None:
        return self.session.get(LLMResponse, entity_id)

    def attach_response(self, response: LLMResponse) -> LLMResponse:
        return self.add(response)

    def delete(self, entity: LLMResponse) -> None:
        self.session.delete(entity)

