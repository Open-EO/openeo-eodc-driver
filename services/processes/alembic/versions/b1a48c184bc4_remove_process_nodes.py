"""remove process_nodes

Revision ID: b1a48c184bc4
Revises: 29a79b69203e
Create Date: 2019-07-09 16:48:31.672077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1a48c184bc4'
down_revision = '29a79b69203e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('process_nodes')


def downgrade():
    # TODO ForeignKeys are properly created
    op.create_table(
        'process_nodes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('seq_num', sa.Integer(), nullable=False),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey("process_graphs.id"), nullable=False),
        sa.Column('process_id', sa.String(), nullable=False),
        sa.Column('imagery_id', sa.String(), sa.ForeignKey("process_nodes.id"), nullable=True),
        sa.Column('args', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
