"""renamed columns with prefixes

Revision ID: 42d6b98cfe7f
Revises: e50e2393920e
Create Date: 2026-05-21 20:45:30.929162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '42d6b98cfe7f'
down_revision: Union[str, Sequence[str], None] = 'e50e2393920e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table)}


def _rename_column_if_needed(table: str, old_name: str, new_name: str) -> None:
    columns = _column_names(table)
    if old_name in columns and new_name not in columns:
        op.alter_column(table, old_name, new_column_name=new_name)


def upgrade() -> None:
    """Rename unprefixed columns when upgrading from older e50e2393920e schemas."""
    for old_name, new_name in (
        ("channel", "tx_channel"),
        ("status", "tx_status"),
        ("attempt_count", "nu_attempt_count"),
        ("last_error", "tx_last_error"),
        ("sent_at", "ts_sent_at"),
        ("created_at", "ts_created_at"),
        ("updated_at", "ts_updated_at"),
    ):
        _rename_column_if_needed("notification_channels", old_name, new_name)

    notification_columns = _column_names("notifications")
    if "id_user" in notification_columns:
        op.alter_column(
            "notifications",
            "id_user",
            existing_type=sa.INTEGER(),
            type_=sa.Text(),
            existing_nullable=False,
            postgresql_using="id_user::text",
        )

    for old_name, new_name in (
        ("aggregate_id", "id_aggregate"),
        ("event_type", "tx_event_type"),
        ("payload", "js_payload"),
        ("status", "tx_status"),
        ("created_at", "ts_created_at"),
        ("published_at", "ts_published_at"),
    ):
        _rename_column_if_needed("outbox_events", old_name, new_name)


def downgrade() -> None:
    """Restore unprefixed column names when they still exist."""
    for old_name, new_name in (
        ("ts_published_at", "published_at"),
        ("ts_created_at", "created_at"),
        ("tx_status", "status"),
        ("js_payload", "payload"),
        ("tx_event_type", "event_type"),
        ("id_aggregate", "aggregate_id"),
    ):
        _rename_column_if_needed("outbox_events", old_name, new_name)

    notification_columns = _column_names("notifications")
    if "id_user" in notification_columns:
        op.alter_column(
            "notifications",
            "id_user",
            existing_type=sa.Text(),
            type_=sa.INTEGER(),
            existing_nullable=False,
            postgresql_using="id_user::integer",
        )

    for old_name, new_name in (
        ("ts_updated_at", "updated_at"),
        ("ts_created_at", "created_at"),
        ("ts_sent_at", "sent_at"),
        ("tx_last_error", "last_error"),
        ("nu_attempt_count", "attempt_count"),
        ("tx_status", "status"),
        ("tx_channel", "channel"),
    ):
        _rename_column_if_needed("notification_channels", old_name, new_name)
