"""improve job data types

Revision ID: 07b769722b91
Revises: db653012e83c
Create Date: 2019-07-16 16:15:52.820566

"""
from alembic import op
import sqlalchemy as sa
import enum


# revision identifiers, used by Alembic.
revision = '07b769722b91'
down_revision = 'db653012e83c'
branch_labels = None
depends_on = None


class JobStatus(enum.Enum):
    def __str__(self):
        return str(self.value)
    submitted = "submitted"
    queued = "queued"
    running = "running"
    canceled = "canceled"
    finished = "finished"
    error = "error"


job_status_options = ("submitted", "queued", "running", "canceled", "finished", "error")
job_status_type = sa.Enum(JobStatus, name='job_status')


def upgrade():
    job_status_type.create(op.get_bind())
    op.alter_column('jobs', 'status', type_=job_status_type, postgresql_using='status::job_status', nullable=False)
    op.alter_column('jobs', 'budget', type_=sa.Float, postgresql_using='budget::float')
    op.alter_column('jobs', 'current_costs', type_=sa.Float, postgresql_using='current_costs::float')


def downgrade():
    op.alter_column('jobs', 'status', type_=sa.String, postgresql_using='status::text', nullable=False)
    op.alter_column('jobs', 'budget', type_=sa.Integer, postgresql_using='budget::integer')
    op.alter_column('jobs', 'current_costs', type_=sa.Integer, postgresql_using='current_costs::integer')
    job_status_type.drop(op.get_bind())
