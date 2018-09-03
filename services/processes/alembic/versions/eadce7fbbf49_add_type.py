"""Added a type for processes

Revision ID: eadce7fbbf49
Revises: e246fb5ed851
Create Date: 2018-08-31 13:24:22.009338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eadce7fbbf49'
down_revision = 'e246fb5ed851'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('processes',
        sa.Column('p_type', sa.String(), default="operation")
    )


def downgrade():
    op.drop_column('processes', 'p_type')
