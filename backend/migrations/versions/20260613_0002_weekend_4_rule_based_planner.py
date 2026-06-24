"""weekend 4 rule based planner tables

Revision ID: 20260613_0002
Revises: 20260607_0001
Create Date: 2026-06-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260613_0002"
down_revision: str | None = "20260607_0001"
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
        "study_plans",
        uuid_pk(),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("active_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["goal_id"], ["study_goals.id"], name=op.f("fk_study_plans_goal_id_study_goals"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_study_plans_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_plans")),
    )
    op.create_index("ix_study_plans_goal_id", "study_plans", ["goal_id"], unique=False)
    op.create_index("ix_study_plans_user_id", "study_plans", ["user_id"], unique=False)
    op.create_index("ix_study_plans_status", "study_plans", ["status"], unique=False)

    op.create_table(
        "study_plan_versions",
        uuid_pk(),
        sa.Column("study_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("version_reason", sa.String(length=100), nullable=False),
        sa.Column("generated_by", sa.String(length=50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["study_plan_id"], ["study_plans.id"], name=op.f("fk_study_plan_versions_study_plan_id_study_plans"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["goal_id"], ["study_goals.id"], name=op.f("fk_study_plan_versions_goal_id_study_goals"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_study_plan_versions_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_plan_versions")),
        sa.UniqueConstraint("study_plan_id", "version_number", name="uq_study_plan_versions_plan_version"),
    )
    op.create_index("ix_study_plan_versions_study_plan_id", "study_plan_versions", ["study_plan_id"], unique=False)
    op.create_index("ix_study_plan_versions_user_id", "study_plan_versions", ["user_id"], unique=False)
    op.create_index("ix_study_plan_versions_is_active", "study_plan_versions", ["is_active"], unique=False)

    op.create_table(
        "study_sessions",
        uuid_pk(),
        sa.Column("study_plan_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("study_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("planned_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("session_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["study_plan_version_id"], ["study_plan_versions.id"], name=op.f("fk_study_sessions_study_plan_version_id_study_plan_versions"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["study_plan_id"], ["study_plans.id"], name=op.f("fk_study_sessions_study_plan_id_study_plans"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["goal_id"], ["study_goals.id"], name=op.f("fk_study_sessions_goal_id_study_goals"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_study_sessions_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_sessions")),
    )
    op.create_index("ix_study_sessions_study_plan_version_id", "study_sessions", ["study_plan_version_id"], unique=False)
    op.create_index("ix_study_sessions_user_id_session_date", "study_sessions", ["user_id", "session_date"], unique=False)
    op.create_index("ix_study_sessions_status", "study_sessions", ["status"], unique=False)
    op.create_index("ix_study_sessions_session_type", "study_sessions", ["session_type"], unique=False)

    op.create_table(
        "study_tasks",
        uuid_pk(),
        sa.Column("study_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("planned_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["study_session_id"], ["study_sessions.id"], name=op.f("fk_study_tasks_study_session_id_study_sessions"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], name=op.f("fk_study_tasks_topic_id_topics"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_study_tasks_subject_id_subjects"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_study_tasks_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_tasks")),
    )
    op.create_index("ix_study_tasks_study_session_id", "study_tasks", ["study_session_id"], unique=False)
    op.create_index("ix_study_tasks_topic_id", "study_tasks", ["topic_id"], unique=False)
    op.create_index("ix_study_tasks_user_id", "study_tasks", ["user_id"], unique=False)
    op.create_index("ix_study_tasks_status", "study_tasks", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_study_tasks_status", table_name="study_tasks")
    op.drop_index("ix_study_tasks_user_id", table_name="study_tasks")
    op.drop_index("ix_study_tasks_topic_id", table_name="study_tasks")
    op.drop_index("ix_study_tasks_study_session_id", table_name="study_tasks")
    op.drop_table("study_tasks")

    op.drop_index("ix_study_sessions_session_type", table_name="study_sessions")
    op.drop_index("ix_study_sessions_status", table_name="study_sessions")
    op.drop_index("ix_study_sessions_user_id_session_date", table_name="study_sessions")
    op.drop_index("ix_study_sessions_study_plan_version_id", table_name="study_sessions")
    op.drop_table("study_sessions")

    op.drop_index("ix_study_plan_versions_is_active", table_name="study_plan_versions")
    op.drop_index("ix_study_plan_versions_user_id", table_name="study_plan_versions")
    op.drop_index("ix_study_plan_versions_study_plan_id", table_name="study_plan_versions")
    op.drop_table("study_plan_versions")

    op.drop_index("ix_study_plans_status", table_name="study_plans")
    op.drop_index("ix_study_plans_user_id", table_name="study_plans")
    op.drop_index("ix_study_plans_goal_id", table_name="study_plans")
    op.drop_table("study_plans")

