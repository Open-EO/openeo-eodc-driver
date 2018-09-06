"""Process Graph JSON column

Revision ID: 76ede68ef627
Revises: e395d5b43047
Create Date: 2018-09-05 11:47:17.206041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76ede68ef627'
down_revision = 'e395d5b43047'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('process_graphs',
        sa.Column('process_graph', sa.JSON(), default={})
    )


def downgrade():
    op.drop_column('process_graphs', 'process_graph')
