"""weekend 5 agent logging tables

Revision ID: 20260613_0003
Revises: 20260613_0002
Create Date: 2026-06-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260613_0003"
down_revision: str | None = "20260613_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False)


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("run_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("output_summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_agent_runs_user_id_users"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_runs")),
    )
    op.create_index("ix_agent_runs_user_id", "agent_runs", ["user_id"], unique=False)
    op.create_index("ix_agent_runs_run_type", "agent_runs", ["run_type"], unique=False)
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"], unique=False)
    op.create_index("ix_agent_runs_entity_type_entity_id", "agent_runs", ["entity_type", "entity_id"], unique=False)

    op.create_table(
        "llm_prompts",
        uuid_pk(),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("prompt_type", sa.String(length=100), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("user_prompt", sa.Text(), nullable=False),
        sa.Column("prompt_version", sa.String(length=20), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"], name=op.f("fk_llm_prompts_agent_run_id_agent_runs"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_llm_prompts")),
    )
    op.create_index("ix_llm_prompts_agent_run_id", "llm_prompts", ["agent_run_id"], unique=False)
    op.create_index("ix_llm_prompts_provider", "llm_prompts", ["provider"], unique=False)
    op.create_index("ix_llm_prompts_prompt_type", "llm_prompts", ["prompt_type"], unique=False)

    op.create_table(
        "llm_responses",
        uuid_pk(),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("llm_prompt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("parsed_response", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"], name=op.f("fk_llm_responses_agent_run_id_agent_runs"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["llm_prompt_id"], ["llm_prompts.id"], name=op.f("fk_llm_responses_llm_prompt_id_llm_prompts"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_llm_responses")),
    )
    op.create_index("ix_llm_responses_agent_run_id", "llm_responses", ["agent_run_id"], unique=False)
    op.create_index("ix_llm_responses_llm_prompt_id", "llm_responses", ["llm_prompt_id"], unique=False)
    op.create_index("ix_llm_responses_status", "llm_responses", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_llm_responses_status", table_name="llm_responses")
    op.drop_index("ix_llm_responses_llm_prompt_id", table_name="llm_responses")
    op.drop_index("ix_llm_responses_agent_run_id", table_name="llm_responses")
    op.drop_table("llm_responses")

    op.drop_index("ix_llm_prompts_prompt_type", table_name="llm_prompts")
    op.drop_index("ix_llm_prompts_provider", table_name="llm_prompts")
    op.drop_index("ix_llm_prompts_agent_run_id", table_name="llm_prompts")
    op.drop_table("llm_prompts")

    op.drop_index("ix_agent_runs_entity_type_entity_id", table_name="agent_runs")
    op.drop_index("ix_agent_runs_status", table_name="agent_runs")
    op.drop_index("ix_agent_runs_run_type", table_name="agent_runs")
    op.drop_index("ix_agent_runs_user_id", table_name="agent_runs")
    op.drop_table("agent_runs")

