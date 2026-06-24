import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class StudyGoal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "study_goals"
    __table_args__ = (
        Index("ix_study_goals_user_id", "user_id"),
        Index("ix_study_goals_status", "status"),
        Index("ix_study_goals_exam_date", "exam_date"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_score: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)

    subjects: Mapped[list["Subject"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"StudyGoal(id={self.id!s}, user_id={self.user_id!s}, status={self.status!r})"


class Subject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subjects"
    __table_args__ = (
        Index("ix_subjects_goal_id", "goal_id"),
        Index("ix_subjects_user_id", "user_id"),
    )

    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_goals.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    goal: Mapped[StudyGoal] = relationship(back_populates="subjects")
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Subject(id={self.id!s}, goal_id={self.goal_id!s}, name={self.name!r})"


class Topic(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "topics"
    __table_args__ = (
        Index("ix_topics_subject_id", "subject_id"),
        Index("ix_topics_goal_id", "goal_id"),
        Index("ix_topics_user_id", "user_id"),
        Index("ix_topics_difficulty", "difficulty"),
        Index("ix_topics_priority", "priority"),
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_goals.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    estimated_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_manually_marked_weak: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    subject: Mapped[Subject] = relationship(back_populates="topics")
    goal: Mapped[StudyGoal] = relationship(back_populates="topics")

    def __repr__(self) -> str:
        return f"Topic(id={self.id!s}, subject_id={self.subject_id!s}, name={self.name!r})"

