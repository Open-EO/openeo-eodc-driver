"""remove process tables

Revision ID: 29a79b69203e
Revises: 76ede68ef627
Create Date: 2019-07-03 15:10:17.546014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29a79b69203e'
down_revision = '76ede68ef627'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('parameters')
    op.drop_table('processes')


def downgrade():
    # TODO ForeignKeys are properly created
    op.create_table(
        'processes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('summary', sa.TEXT(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=False),
        sa.Column('min_parameters', sa.Integer(), nullable=True),
        sa.Column('returns', sa.JSON(), nullable=False),
        sa.Column('deprecated', sa.Boolean(), default=False),
        sa.Column('exceptions', sa.JSON(), nullable=True),
        sa.Column('examples', sa.JSON(), nullable=True),
        sa.Column('links', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('p_type', sa.String(), default="operation"),
    )
    op.create_table(
        'parameters',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('process_id', sa.String(), sa.ForeignKey("processes.id"), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=False),
        sa.Column('required', sa.Boolean(), default=False),
        sa.Column('deprecated', sa.Boolean(), default=False),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('schema', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
