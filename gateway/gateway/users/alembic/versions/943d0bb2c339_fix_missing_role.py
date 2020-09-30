"""fix missing role.

Revision ID: 943d0bb2c339
Revises: 005b10e50392
Create Date: 2019-12-17 16:42:35.258176
"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '943d0bb2c339'
down_revision = '005b10e50392'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade DB model.

    Add column users.role to store user role (user / admin).
    """
    op.add_column('users', sa.Column('role', sa.Text, nullable=False, default='user'))


def downgrade() -> None:
    """Downgrade DB model.

    Drop column users.role.
    """
    op.drop_column('users', 'role')
