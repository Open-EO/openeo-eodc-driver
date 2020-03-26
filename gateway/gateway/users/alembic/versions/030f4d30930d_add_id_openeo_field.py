"""add id_openeo field

Revision ID: 030f4d30930d
Revises: 1efc54cd3649
Create Date: 2019-12-16 13:59:38.776475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '030f4d30930d'
down_revision = '1efc54cd3649'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('identity_providers',
        sa.Column('id_openeo', sa.String(), nullable=False, unique=True)
    )


def downgrade():
    op.drop_column('identity_providers', 'id_openeo')
