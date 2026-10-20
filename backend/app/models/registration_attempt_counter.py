from datetime import datetime

from sqlalchemy import DateTime, Integer, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import INET

from app.db.base import Base

class RegistrationAttemptCounter(Base):
    __tablename__ = "auth_registration_attempt_counters"

    client_ip: Mapped[str] = mapped_column(
        INET,
        primary_key=True
    )

    window_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True
    )

    window_seconds: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "window_seconds > 0",
            name="ck_registration_window_positive",
        ),
        CheckConstraint(
            "attempt_count > 0",
            name="ck_registration_attempt_count_positive",
        ),
        Index(
            "ix_auth_registration_attempt_counters_window_started_at",
            "window_started_at",
        ),
    )