"""add outbox retry columns

Revision ID: 6f8f9d2b04a1
Revises: 1116845fdec8
Create Date: 2026-06-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6f8f9d2b04a1"
down_revision: Union[str, Sequence[str], None] = "1116845fdec8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "outbox_events",
        sa.Column("nu_attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "outbox_events",
        sa.Column("tx_last_error", sa.String(), nullable=True),
    )
    op.add_column(
        "outbox_events",
        sa.Column("ts_next_retry_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_outbox_events_status_next_retry",
        "outbox_events",
        ["tx_status", "ts_next_retry_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_outbox_events_status_next_retry", table_name="outbox_events")
    op.drop_column("outbox_events", "ts_next_retry_at")
    op.drop_column("outbox_events", "tx_last_error")
    op.drop_column("outbox_events", "nu_attempt_count")
