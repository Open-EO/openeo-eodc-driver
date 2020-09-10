"""remove dag-filename

Revision ID: 52491f474ed8
Revises: ef96f38771a5
Create Date: 2020-09-09 17:23:23.507036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52491f474ed8'
down_revision = 'ef96f38771a5'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('jobs', 'dag_filename')


def downgrade():
    op.add_column('jobs', sa.Column('dag_filename', sa.String(), nullable=True))

