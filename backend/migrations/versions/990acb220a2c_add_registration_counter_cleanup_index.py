"""add registration counter cleanup index

Revision ID: 990acb220a2c
Revises: b547339f2a88
Create Date: 2026-10-20 17:34:25.250402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '990acb220a2c'
down_revision: Union[str, Sequence[str], None] = 'b547339f2a88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_auth_registration_attempt_counters_window_started_at",
        "auth_registration_attempt_counters",
        ["window_started_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_auth_registration_attempt_counters_window_started_at",
        table_name="auth_registration_attempt_counters",
    )
