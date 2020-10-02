"""remove metrics

Revision ID: 9b1e32fde197
Revises: 52491f474ed8
Create Date: 2020-09-24 09:36:40.145148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b1e32fde197'
down_revision = '52491f474ed8'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('jobs', 'metrics')


def downgrade():
    op.add_column('jobs', sa.Column('metrics', sa.JSON(), nullable=True))
