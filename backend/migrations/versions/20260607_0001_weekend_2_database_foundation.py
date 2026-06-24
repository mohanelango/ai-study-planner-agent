"""weekend 2 database foundation

Revision ID: 20260607_0001
Revises:
Create Date: 2026-06-07
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260607_0001"
down_revision: str | None = None
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
        "users",
        uuid_pk(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"], unique=False)

    op.create_table(
        "student_profiles",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("education_level", sa.String(length=100), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=False),
        sa.Column("preferred_study_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("learning_style", sa.String(length=100), nullable=True),
        sa.Column("daily_goal_minutes", sa.Integer(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_student_profiles_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_student_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_student_profiles_user_id")),
    )
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"], unique=False)

    op.create_table(
        "availability_windows",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_availability_windows_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_availability_windows")),
    )
    op.create_index("ix_availability_windows_user_id", "availability_windows", ["user_id"], unique=False)
    op.create_index("ix_availability_windows_user_id_day_of_week", "availability_windows", ["user_id", "day_of_week"], unique=False)

    op.create_table(
        "study_goals",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=False),
        sa.Column("target_score", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_study_goals_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_goals")),
    )
    op.create_index("ix_study_goals_user_id", "study_goals", ["user_id"], unique=False)
    op.create_index("ix_study_goals_status", "study_goals", ["status"], unique=False)
    op.create_index("ix_study_goals_exam_date", "study_goals", ["exam_date"], unique=False)

    op.create_table(
        "subjects",
        uuid_pk(),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["goal_id"], ["study_goals.id"], name=op.f("fk_subjects_goal_id_study_goals"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_subjects_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subjects")),
    )
    op.create_index("ix_subjects_goal_id", "subjects", ["goal_id"], unique=False)
    op.create_index("ix_subjects_user_id", "subjects", ["user_id"], unique=False)

    op.create_table(
        "topics",
        uuid_pk(),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("estimated_hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("is_manually_marked_weak", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_topics_subject_id_subjects"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["goal_id"], ["study_goals.id"], name=op.f("fk_topics_goal_id_study_goals"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_topics_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_topics")),
    )
    op.create_index("ix_topics_subject_id", "topics", ["subject_id"], unique=False)
    op.create_index("ix_topics_goal_id", "topics", ["goal_id"], unique=False)
    op.create_index("ix_topics_user_id", "topics", ["user_id"], unique=False)
    op.create_index("ix_topics_difficulty", "topics", ["difficulty"], unique=False)
    op.create_index("ix_topics_priority", "topics", ["priority"], unique=False)

    op.create_table(
        "background_jobs",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
        sa.Column("input_payload", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("result_payload", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_background_jobs_user_id_users"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_background_jobs")),
    )
    op.create_index("ix_background_jobs_user_id", "background_jobs", ["user_id"], unique=False)
    op.create_index("ix_background_jobs_job_type", "background_jobs", ["job_type"], unique=False)
    op.create_index("ix_background_jobs_status", "background_jobs", ["status"], unique=False)
    op.create_index("ix_background_jobs_entity_type_entity_id", "background_jobs", ["entity_type", "entity_id"], unique=False)
    op.create_index("ix_background_jobs_celery_task_id", "background_jobs", ["celery_task_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_background_jobs_celery_task_id", table_name="background_jobs")
    op.drop_index("ix_background_jobs_entity_type_entity_id", table_name="background_jobs")
    op.drop_index("ix_background_jobs_status", table_name="background_jobs")
    op.drop_index("ix_background_jobs_job_type", table_name="background_jobs")
    op.drop_index("ix_background_jobs_user_id", table_name="background_jobs")
    op.drop_table("background_jobs")

    op.drop_index("ix_topics_priority", table_name="topics")
    op.drop_index("ix_topics_difficulty", table_name="topics")
    op.drop_index("ix_topics_user_id", table_name="topics")
    op.drop_index("ix_topics_goal_id", table_name="topics")
    op.drop_index("ix_topics_subject_id", table_name="topics")
    op.drop_table("topics")

    op.drop_index("ix_subjects_user_id", table_name="subjects")
    op.drop_index("ix_subjects_goal_id", table_name="subjects")
    op.drop_table("subjects")

    op.drop_index("ix_study_goals_exam_date", table_name="study_goals")
    op.drop_index("ix_study_goals_status", table_name="study_goals")
    op.drop_index("ix_study_goals_user_id", table_name="study_goals")
    op.drop_table("study_goals")

    op.drop_index("ix_availability_windows_user_id_day_of_week", table_name="availability_windows")
    op.drop_index("ix_availability_windows_user_id", table_name="availability_windows")
    op.drop_table("availability_windows")

    op.drop_index("ix_student_profiles_user_id", table_name="student_profiles")
    op.drop_table("student_profiles")

    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

