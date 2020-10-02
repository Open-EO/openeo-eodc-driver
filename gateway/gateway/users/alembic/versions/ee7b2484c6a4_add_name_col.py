"""add_name_col.

Revision ID: ee7b2484c6a4
Revises: 06082d6cce6b
Create Date: 2020-09-08 18:09:29.124892

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'ee7b2484c6a4'
down_revision = '06082d6cce6b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade DB model.

    Add column users.name - to have a human-friendly display name.
    """
    op.add_column('users', sa.Column('name', sa.Text, nullable=True))


def downgrade() -> None:
    """Downgrade DB model.

    Drop column users.name.
    """
    op.drop_column('users', 'name')
