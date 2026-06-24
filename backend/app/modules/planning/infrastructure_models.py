import uuid
from datetime import date, time

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class StudyPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "study_plans"
    __table_args__ = (
        Index("ix_study_plans_goal_id", "goal_id"),
        Index("ix_study_plans_user_id", "user_id"),
        Index("ix_study_plans_status", "status"),
    )

    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_goals.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    active_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    versions: Mapped[list["StudyPlanVersion"]] = relationship(back_populates="study_plan", cascade="all, delete-orphan")
    sessions: Mapped[list["StudySession"]] = relationship(back_populates="study_plan", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"StudyPlan(id={self.id!s}, goal_id={self.goal_id!s}, status={self.status!r})"


class StudyPlanVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "study_plan_versions"
    __table_args__ = (
        UniqueConstraint("study_plan_id", "version_number", name="uq_study_plan_versions_plan_version"),
        Index("ix_study_plan_versions_study_plan_id", "study_plan_id"),
        Index("ix_study_plan_versions_user_id", "user_id"),
        Index("ix_study_plan_versions_is_active", "is_active"),
    )

    study_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_goals.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version_reason: Mapped[str] = mapped_column(String(100), default="initial_generation", nullable=False)
    generated_by: Mapped[str] = mapped_column(String(50), default="system", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    study_plan: Mapped[StudyPlan] = relationship(back_populates="versions")
    sessions: Mapped[list["StudySession"]] = relationship(back_populates="version", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"StudyPlanVersion(id={self.id!s}, plan_id={self.study_plan_id!s}, version={self.version_number!r})"


class StudySession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "study_sessions"
    __table_args__ = (
        Index("ix_study_sessions_study_plan_version_id", "study_plan_version_id"),
        Index("ix_study_sessions_user_id_session_date", "user_id", "session_date"),
        Index("ix_study_sessions_status", "status"),
        Index("ix_study_sessions_session_type", "session_type"),
    )

    study_plan_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_plan_versions.id", ondelete="CASCADE"), nullable=False)
    study_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_goals.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_date: Mapped[date] = mapped_column(nullable=False)
    start_time: Mapped[time | None] = mapped_column(nullable=True)
    end_time: Mapped[time | None] = mapped_column(nullable=True)
    planned_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    session_type: Mapped[str] = mapped_column(String(50), default="study", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False)

    study_plan: Mapped[StudyPlan] = relationship(back_populates="sessions")
    version: Mapped[StudyPlanVersion] = relationship(back_populates="sessions")
    tasks: Mapped[list["StudyTask"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class StudyTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "study_tasks"
    __table_args__ = (
        Index("ix_study_tasks_study_session_id", "study_session_id"),
        Index("ix_study_tasks_topic_id", "topic_id"),
        Index("ix_study_tasks_user_id", "user_id"),
        Index("ix_study_tasks_status", "status"),
    )

    study_session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    subject_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), default="learn", nullable=False)
    planned_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped[StudySession] = relationship(back_populates="tasks")

