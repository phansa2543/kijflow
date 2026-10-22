"""add login attempt counters

Revision ID: 8c29892d0406
Revises: 990acb220a2c
Create Date: 2026-10-22 10:55:37.799314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c29892d0406'
down_revision: Union[str, Sequence[str], None] = '990acb220a2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "auth_login_attempt_counters",
        sa.Column("dimension", sa.Text(), nullable=False),
        sa.Column("identifier", sa.Text(), nullable=False),
        sa.Column(
            "window_started_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column("window_seconds", sa.Integer(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint(
            "dimension",
            "identifier",
            "window_started_at",
            "window_seconds",
            name="pk_auth_login_attempt_counters"
        ),
        sa.CheckConstraint(
            "dimension IN ('ACCOUNT', 'SOURCE')",
            name="ck_auth_login_counter_dimension"
        ),
        sa.CheckConstraint(
            "identifier <> ''",
            name="ck_auth_login_counter_identifier"
        ),
        sa.CheckConstraint(
            "window_seconds > 0",
            name="ck_auth_login_counter_window_seconds"
        ),
        sa.CheckConstraint(
            "attempt_count >= 0",
            name="ck_auth_login_counter_attempt_count"
        )
    )

    op.create_index(
        "ix_auth_login_counter_window_started_at",
        "auth_login_attempt_counters",
        ["window_started_at"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_auth_login_counter_window_started_at",
        table_name="auth_login_attempt_counters"
    )

    op.drop_table("auth_login_attempt_counters")