"""add conflicto_fechas to cotizaciones

Revision ID: 133a17f92fe7
Revises:
Create Date: 2026-07-13 22:11:46.468351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '133a17f92fe7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'cotizaciones',
        sa.Column('conflicto_fechas', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('cotizaciones', 'conflicto_fechas')
