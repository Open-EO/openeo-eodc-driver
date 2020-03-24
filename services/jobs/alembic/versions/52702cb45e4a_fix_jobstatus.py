"""fix jobstatus

Revision ID: 52702cb45e4a
Revises: 07b769722b91
Create Date: 2020-03-24 17:01:21.270670

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52702cb45e4a'
down_revision = '07b769722b91'
branch_labels = None
depends_on = None


old_options = ('submitted', 'queued', 'running', 'canceled', 'finished', 'error')
new_options = ('created', 'queued', 'running', 'canceled', 'finished', 'error')

old_type = sa.Enum(*old_options, name='job_status')
new_type = sa.Enum(*new_options, name='job_status')


def upgrade():
    op.alter_column('jobs', 'status', type_=sa.String, postgresql_using='status::text')
    old_type.drop(op.get_bind(), checkfirst=False)
    new_type.create(op.get_bind(), checkfirst=False)
    op.execute("UPDATE jobs SET status='created' WHERE status = 'submitted'")
    op.alter_column('jobs', 'status', type_=new_type, postgresql_using='status::job_status')

    jobs = sa.table('jobs', sa.column('budget'))
    op.execute(jobs.update().values(budget=sa.column('budget')*100))
    jobs = sa.table('jobs', sa.column('current_costs'))
    op.execute(jobs.update().values(current_costs=sa.column('current_costs')*100))
    op.alter_column('jobs', 'budget', type_=sa.Integer, postgresql_using='budget::integer')
    op.alter_column('jobs', 'current_costs', type_=sa.Integer, postgresql_using='current_costs::integer')


def downgrade():
    op.alter_column('jobs', 'status', type_=sa.String, postgresql_using='status::text')
    new_type.drop(op.get_bind(), checkfirst=False)
    old_type.create(op.get_bind(), checkfirst=False)
    op.execute("UPDATE jobs SET status='submitted' WHERE status = 'created'")
    op.alter_column('jobs', 'status', type_=new_type, postgresql_using='status::job_status')

    op.alter_column('jobs', 'budget', type_=sa.Float, postgresql_using='budget::float')
    op.alter_column('jobs', 'current_costs', type_=sa.Float, postgresql_using='current_costs::float')
    jobs = sa.table('jobs', sa.column('budget'))
    op.execute(jobs.update().values(budget=sa.column('budget')/100.))
    jobs = sa.table('jobs', sa.column('current_costs'))
    op.execute(jobs.update().values(current_costs=sa.column('current_costs')/100.))
