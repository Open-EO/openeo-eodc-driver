"""Initial process, process_graph and process_node models

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
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    op.create_table(
        'process_graphs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    op.create_table(
        'process_nodes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('seq_num', sa.Integer(), nullable=False),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey("process_graphs.id"), nullable=False),
        sa.Column('process_id', sa.String(), sa.ForeignKey("processes.id"), nullable=False),
        sa.Column('imagery_id', sa.String(), sa.ForeignKey("process_nodes.id"), nullable=True),
        sa.Column('product_id', sa.String(), nullable=True),
        sa.Column('args', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
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

def downgrade():
    op.drop_table('parameters')
    op.drop_table('process_nodes')
    op.drop_table('process_graphs')
    op.drop_table('processes')
