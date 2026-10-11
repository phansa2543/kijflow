import uuid
from datetime import datetime

from sqlalchemy import UUID, ForeignKey, DateTime, func, Text, CheckConstraint, UniqueConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False
    )

    profile: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "profile IN ('OWNER', 'ADMIN', 'MEMBER')",
            name="ck_memberships_profile_valid",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'DISABLED', 'REVOKED')",
            name="ck_memberships_status_valid",
        ),
        CheckConstraint(
            "profile <> 'OWNER' OR status = 'ACTIVE'",
            name="ck_memberships_owner_must_be_active",
        ),
        UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_memberships_user_organization",
        ),
        Index(
            "ix_memberships_organization_id",
            "organization_id",
        ),
        Index(
            "uq_memberships_one_owner_per_organization",
            "organization_id",
            unique=True,
            postgresql_where=text("profile = 'OWNER'"),
        ),
    )