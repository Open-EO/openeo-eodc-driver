"""fix missing role

Revision ID: 943d0bb2c339
Revises: 005b10e50392
Create Date: 2019-12-17 16:42:35.258176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '943d0bb2c339'
down_revision = '005b10e50392'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('role', sa.Text, nullable=False, default='user'))


def downgrade():
    op.drop_columns('users', 'role')
