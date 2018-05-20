"""Initial jobs database

Revision ID: 9e0975c7737a
Revises: 
Create Date: 2018-05-11 15:14:10.010760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e0975c7737a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), default="submitted", nullable=False),
        sa.Column('credits', sa.Integer(), default=0, nullable=False),
        sa.Column('process_graph', sa.JSON, nullable=True),
        sa.Column('output', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(),
                  onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey(
            "jobs.id"), nullable=False),
        sa.Column('process_id', sa.String(), nullable=False),
        sa.Column('seq_num', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(),
                  default="initialized", nullable=False),
        # sa.Column('next', sa.Integer(), sa.ForeignKey(
        #     "tasks.id"), nullable=True),
        sa.Column('args', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(),
                  onupdate=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table('tasks')
    op.drop_table('jobs')
    