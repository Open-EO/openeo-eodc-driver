"""add remove job columns

Revision ID: db653012e83c
Revises: 2e488b097c11
Create Date: 2019-07-16 13:22:59.810454

"""
from alembic import op
import sqlalchemy as sa
import json


# revision identifiers, used by Alembic.
revision = 'db653012e83c'
down_revision = '2e488b097c11'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('jobs', 'output')

    op.add_column('jobs', sa.Column('progress', sa.INT(), nullable=True))
    op.add_column('jobs', sa.Column('error', sa.JSON(), nullable=True))


def downgrade():
    op.add_column('jobs', sa.Column('output', sa.JSON(), default=json.dumps({"format": "GTiff"})))

    op.drop_column('jobs', 'progress')
    op.drop_column('jobs', 'error')
