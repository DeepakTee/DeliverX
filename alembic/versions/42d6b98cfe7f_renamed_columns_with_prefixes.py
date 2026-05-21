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


def upgrade() -> None:
    """Rename unprefixed columns to prefixed names (preserves existing row data)."""
    op.alter_column(
        'notification_channels',
        'channel',
        new_column_name='tx_channel',
    )
    op.alter_column(
        'notification_channels',
        'status',
        new_column_name='tx_status',
    )
    op.alter_column(
        'notification_channels',
        'attempt_count',
        new_column_name='nu_attempt_count',
    )
    op.alter_column(
        'notification_channels',
        'last_error',
        new_column_name='tx_last_error',
    )
    op.alter_column(
        'notification_channels',
        'sent_at',
        new_column_name='ts_sent_at',
    )
    op.alter_column(
        'notification_channels',
        'created_at',
        new_column_name='ts_created_at',
    )
    op.alter_column(
        'notification_channels',
        'updated_at',
        new_column_name='ts_updated_at',
    )

    op.alter_column(
        'notifications',
        'id_user',
        existing_type=sa.INTEGER(),
        type_=sa.Text(),
        existing_nullable=False,
        postgresql_using='id_user::text',
    )

    op.alter_column(
        'outbox_events',
        'aggregate_id',
        new_column_name='id_aggregate',
    )
    op.alter_column(
        'outbox_events',
        'event_type',
        new_column_name='tx_event_type',
    )
    op.alter_column(
        'outbox_events',
        'payload',
        new_column_name='js_payload',
    )
    op.alter_column(
        'outbox_events',
        'status',
        new_column_name='tx_status',
    )
    op.alter_column(
        'outbox_events',
        'created_at',
        new_column_name='ts_created_at',
    )
    op.alter_column(
        'outbox_events',
        'published_at',
        new_column_name='ts_published_at',
    )


def downgrade() -> None:
    """Restore unprefixed column names."""
    op.alter_column(
        'outbox_events',
        'ts_published_at',
        new_column_name='published_at',
    )
    op.alter_column(
        'outbox_events',
        'ts_created_at',
        new_column_name='created_at',
    )
    op.alter_column(
        'outbox_events',
        'tx_status',
        new_column_name='status',
    )
    op.alter_column(
        'outbox_events',
        'js_payload',
        new_column_name='payload',
    )
    op.alter_column(
        'outbox_events',
        'tx_event_type',
        new_column_name='event_type',
    )
    op.alter_column(
        'outbox_events',
        'id_aggregate',
        new_column_name='aggregate_id',
    )

    op.alter_column(
        'notifications',
        'id_user',
        existing_type=sa.Text(),
        type_=sa.INTEGER(),
        existing_nullable=False,
        postgresql_using='id_user::integer',
    )

    op.alter_column(
        'notification_channels',
        'ts_updated_at',
        new_column_name='updated_at',
    )
    op.alter_column(
        'notification_channels',
        'ts_created_at',
        new_column_name='created_at',
    )
    op.alter_column(
        'notification_channels',
        'ts_sent_at',
        new_column_name='sent_at',
    )
    op.alter_column(
        'notification_channels',
        'tx_last_error',
        new_column_name='last_error',
    )
    op.alter_column(
        'notification_channels',
        'nu_attempt_count',
        new_column_name='attempt_count',
    )
    op.alter_column(
        'notification_channels',
        'tx_status',
        new_column_name='status',
    )
    op.alter_column(
        'notification_channels',
        'tx_channel',
        new_column_name='channel',
    )
