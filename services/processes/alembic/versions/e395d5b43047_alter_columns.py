"""alter columns

Revision ID: e395d5b43047
Revises: eadce7fbbf49
Create Date: 2018-08-31 15:11:52.052420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e395d5b43047'
down_revision = 'eadce7fbbf49'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('process_nodes', 'process_id')
    op.add_column('process_nodes',
        sa.Column('process_id', sa.String(), nullable=False)
    )
    op.drop_column('process_nodes', 'product_id')


def downgrade():
    op.drop_column('process_nodes', 'process_id')
    op.add_column('process_nodes',
        sa.Column('process_id', sa.String(), sa.ForeignKey("processes.id"), nullable=False)
    )
    op.add_column('process_nodes',
        sa.Column('product_id', sa.String(), nullable=True)
    )
