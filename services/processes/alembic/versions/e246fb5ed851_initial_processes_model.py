"""Initial processes model

Revision ID: e246fb5ed851
Revises: 
Create Date: 2018-05-15 10:05:54.708107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e246fb5ed851'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'processes',
        sa.Column('process_id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=False),
        sa.Column('process_type', sa.String(), nullable=False),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('args', sa.JSON(), nullable=True),
        sa.Column('git_uri', sa.String(), nullable=True),
        sa.Column('git_ref', sa.String(), nullable=True),
        sa.Column('git_dir', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('processes')
