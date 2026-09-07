"""add duplicate detection fields to claims

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-07 01:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('claims',
        sa.Column('is_potential_duplicate', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.add_column('claims',
        sa.Column('duplicate_of_claim_id', sa.Integer(), sa.ForeignKey('claims.id', ondelete='SET NULL'), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('claims', 'duplicate_of_claim_id')
    op.drop_column('claims', 'is_potential_duplicate')
