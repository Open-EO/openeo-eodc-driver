"""add_flags

Revision ID: f8ee87997081
Revises: 9b1e32fde197
Create Date: 2020-10-08 18:31:31.880893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8ee87997081'
down_revision = '9b1e32fde197'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('jobs', sa.Column('vrt_flag', sa.Boolean, default=True))
    job_vrt = sa.table('jobs', sa.column('vrt_flag'))
    op.execute(job_vrt.update().values(vrt_flag=True))
    op.alter_column('jobs', 'vrt_flag', nullable=False)

    op.add_column('jobs', sa.Column('add_parallel_sensor', sa.Boolean, default=True))
    job_parallel = sa.table('jobs', sa.column('add_parallel_sensor'))
    op.execute(job_parallel.update().values(add_parallel_sensor=True))
    op.alter_column('jobs', 'add_parallel_sensor', nullable=False)


def downgrade():
    op.drop_column('jobs', 'vrt_flag')
    op.drop_column('jobs', 'add_parallel_sensor')
