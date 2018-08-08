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
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('summary', sa.TEXT(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('min_parameters', sa.Integer(), nullable=True),
        sa.Column('returns', sa.JSON(), nullable=False),
        sa.Column('deprecated', sa.Boolean(), default=False),
        sa.Column('exceptions', sa.JSON(), nullable=True),
        sa.Column('examples', sa.JSON(), nullable=True),
        sa.Column('links', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('processes')
