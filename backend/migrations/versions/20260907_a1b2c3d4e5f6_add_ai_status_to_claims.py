"""add ai_status to claims

Revision ID: a1b2c3d4e5f6
Revises: 6ab913cd907d
Create Date: 2026-09-07 00:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6ab913cd907d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ai_status_enum = sa.Enum('pending', 'processing', 'completed', 'failed', name='aistatus')
    ai_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'claims',
        sa.Column('ai_status', ai_status_enum, nullable=False, server_default='pending'),
    )

    # Backfill existing rows: completed if AI ran successfully, failed otherwise.
    op.execute(
        "UPDATE claims SET ai_status = CASE WHEN ai_summary IS NOT NULL"
        " THEN 'completed'::aistatus ELSE 'failed'::aistatus END"
    )


def downgrade() -> None:
    op.drop_column('claims', 'ai_status')
    sa.Enum(name='aistatus').drop(op.get_bind(), checkfirst=True)
