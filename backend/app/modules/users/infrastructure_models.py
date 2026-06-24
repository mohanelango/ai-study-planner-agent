import uuid
from datetime import time

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_is_active", "is_active"),
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    availability_windows: Mapped[list["AvailabilityWindow"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!s}, email={self.email!r}, is_active={self.is_active!r})"


class StudentProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "student_profiles"
    __table_args__ = (Index("ix_student_profiles_user_id", "user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    education_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(100), default="Asia/Kolkata", nullable=False)
    preferred_study_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    learning_style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    daily_goal_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"StudentProfile(id={self.id!s}, user_id={self.user_id!s})"


class AvailabilityWindow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "availability_windows"
    __table_args__ = (
        Index("ix_availability_windows_user_id", "user_id"),
        Index("ix_availability_windows_user_id_day_of_week", "user_id", "day_of_week"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship(back_populates="availability_windows")

    def __repr__(self) -> str:
        return f"AvailabilityWindow(id={self.id!s}, user_id={self.user_id!s}, day_of_week={self.day_of_week!r})"

