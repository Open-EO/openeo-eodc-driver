"""clean up

Revision ID: 005b10e50392
Revises: 17295e67b0c5
Create Date: 2019-12-17 15:27:39.956828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005b10e50392'
down_revision = '17295e67b0c5'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fkey_identity_provider_user', 'users', type_='foreignkey')
    op.alter_column('users', 'identity_provider_id', type_=sa.String)
    op.alter_column('identity_providers', 'id', type_=sa.String)
    op.create_foreign_key('fkey_identity_provider_user', 'users', 'identity_providers', ['identity_provider_id'], ['id'])

    op.drop_constraint('users_password_hash_key', 'users', type_='unique')
    op.create_unique_constraint('users_email_key', 'users', ['email'])


def downgrade():

    op.drop_constraint('fkey_identity_provider_user', 'users', type_='foreignkey')
    op.alter_column('users', 'identity_provider_id', type_=sa.Integer, postgresql_using="identity_provider_id::integer")
    op.alter_column('identity_providers', 'id', type_=sa.Integer,postgresql_using="id::integer")
    op.create_foreign_key('fkey_identity_provider_user', 'users', 'identity_providers', ['identity_provider_id'], ['id'])

    op.create_unique_constraint('users_password_hash_key', 'users', ['password_hash'])
    op.drop_constraint('users_email_key', 'users', type_='unique')
