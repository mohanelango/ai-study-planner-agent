import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        Index("ix_agent_runs_user_id", "user_id"),
        Index("ix_agent_runs_run_type", "run_type"),
        Index("ix_agent_runs_status", "status"),
        Index("ix_agent_runs_entity_type_entity_id", "entity_type", "entity_id"),
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    run_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="started", nullable=False)
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    prompts: Mapped[list["LLMPrompt"]] = relationship(back_populates="agent_run", cascade="all, delete-orphan")
    responses: Mapped[list["LLMResponse"]] = relationship(back_populates="agent_run", cascade="all, delete-orphan")


class LLMPrompt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "llm_prompts"
    __table_args__ = (
        Index("ix_llm_prompts_agent_run_id", "agent_run_id"),
        Index("ix_llm_prompts_provider", "provider"),
        Index("ix_llm_prompts_prompt_type", "prompt_type"),
    )

    agent_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="openai", nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_type: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(20), default="v1", nullable=False)

    agent_run: Mapped[AgentRun] = relationship(back_populates="prompts")
    responses: Mapped[list["LLMResponse"]] = relationship(back_populates="llm_prompt", cascade="all, delete-orphan")


class LLMResponse(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "llm_responses"
    __table_args__ = (
        Index("ix_llm_responses_agent_run_id", "agent_run_id"),
        Index("ix_llm_responses_llm_prompt_id", "llm_prompt_id"),
        Index("ix_llm_responses_status", "status"),
    )

    agent_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    llm_prompt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("llm_prompts.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="openai", nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    agent_run: Mapped[AgentRun] = relationship(back_populates="responses")
    llm_prompt: Mapped[LLMPrompt] = relationship(back_populates="responses")

