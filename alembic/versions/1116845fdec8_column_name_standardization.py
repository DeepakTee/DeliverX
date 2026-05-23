"""column name standardization

Revision ID: 1116845fdec8
Revises: 42d6b98cfe7f
Create Date: 2026-05-23 12:31:27.935999

"""
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import Text
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1116845fdec8'
down_revision: Union[str, Sequence[str], None] = '42d6b98cfe7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'notifications',
        'status',
        new_column_name='tx_status',
    )
    op.alter_column(
        'notifications',
        'id_user',
        type_=Text,
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'notifications',
        'tx_status',
        new_column_name='status',
    )
    op.alter_column(
        'notifications',
        'id_user',
        type_=Integer,
    )