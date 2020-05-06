"""add dag_filename

Revision ID: 55fecf5bdaa9
Revises: 52702cb45e4a
Create Date: 2020-03-31 16:28:41.458471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55fecf5bdaa9'
down_revision = '52702cb45e4a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('jobs', sa.Column('dag_filename', sa.String(), nullable=True))


def downgrade():
    op.drop_column('jobs', 'dag_filename')
