"""identity_provider_add_missing_constraints

Revision ID: e877d29a581f
Revises: 943d0bb2c339
Create Date: 2020-02-20 16:09:40.354721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e877d29a581f'
down_revision = '943d0bb2c339'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('identity_providers_id_openeo_key', 'identity_providers', ['id_openeo'])


def downgrade():
    op.drop_constraint('identity_providers_id_openeo_key', 'identity_providers', type_='unique')

