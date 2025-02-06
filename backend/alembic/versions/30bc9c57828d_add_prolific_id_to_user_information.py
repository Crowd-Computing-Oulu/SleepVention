"""Add prolific_id to user_information

Revision ID: 30bc9c57828d
Revises: 
Create Date: 2025-02-06 15:28:19.963726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30bc9c57828d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new column
    op.add_column('user_information', sa.Column('prolific_id', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove the column if we rollback
    op.drop_column('user_information', 'prolific_id')
