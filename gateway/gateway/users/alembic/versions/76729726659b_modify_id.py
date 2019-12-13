"""modify_id

Revision ID: 76729726659b
Revises: 1efc54cd3649
Create Date: 2019-12-13 16:13:08.601905

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76729726659b'
down_revision = '1efc54cd3649'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fkey_identity_provider_user', 'users', type_='foreignkey')
    op.drop_column('identity_providers', 'id')
    op.add_column('identity_providers',
        sa.Column('id', sa.String(), nullable=False, unique=True)
    )
    op.add_column('identity_providers',
        sa.Column('id_internal', sa.Integer, primary_key=True)
    )
    #op.create_foreign_key('fkey_identity_provider_user', 'users', 'identity_providers', ['identity_provider_id'], ['id_internal'])


def downgrade():
    #op.drop_constraint('fkey_identity_provider_user', 'users', type_='foreignkey')
    op.drop_column('identity_providers', 'id')
    op.add_column('identity_providers',
        sa.Column('id', sa.Integer, primary_key=True)
    )
    op.create_foreign_key('fkey_identity_provider_user', 'users', 'identity_providers', ['identity_provider_id'], ['id'])
    op.drop_column('identity_providers', 'id_internal')
