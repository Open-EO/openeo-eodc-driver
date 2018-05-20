"""create users table

Revision ID: c6ae5dd90a29
Revises: 
Create Date: 2018-05-04 16:33:33.595629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6ae5dd90a29'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('active', sa.Boolean(), default=False, nullable=False),
        sa.Column('project', sa.String(), nullable=False),
        sa.Column('sa_token', sa.Text(), nullable=False),
        sa.Column('admin', sa.Boolean(), default=False, nullable=False)
    )


def downgrade():
    op.drop_table('users')
