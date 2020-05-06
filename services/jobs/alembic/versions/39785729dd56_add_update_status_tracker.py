"""add update status tracker

Revision ID: 39785729dd56
Revises: 55fecf5bdaa9
Create Date: 2020-04-14 09:48:04.492840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39785729dd56'
down_revision = '55fecf5bdaa9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('jobs', sa.Column('status_updated_at', sa.DateTime()))
    job_updated = sa.table('jobs', sa.column('status_updated_at'))
    op.execute(job_updated.update().values(status_updated_at=sa.column('updated_at')))
    op.alter_column('jobs', 'status_updated_at', nullable=False)


def downgrade():
    op.drop_column('jobs', 'status_updated_at')
