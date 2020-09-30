"""clean up.

Revision ID: 005b10e50392
Revises: 17295e67b0c5
Create Date: 2019-12-17 15:27:39.956828
"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '005b10e50392'
down_revision = '17295e67b0c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade DB model.

    1. Change identity_provider.id and related ForeignKeys to type string.
    2. Remove unique constraint on users.password_hash - allow corner cases which produce same password.
    3. Set an unique constraint on users.email - used for identification.
    """
    op.drop_constraint('fkey_identity_provider_user', 'users', type_='foreignkey')
    op.alter_column('users', 'identity_provider_id', type_=sa.String)
    op.alter_column('identity_providers', 'id', type_=sa.String)
    op.create_foreign_key('fkey_identity_provider_user', 'users', 'identity_providers', ['identity_provider_id'], ['id'])

    op.drop_constraint('users_password_hash_key', 'users', type_='unique')
    op.create_unique_constraint('users_email_key', 'users', ['email'])


def downgrade() -> None:
    """Downgrade DB model.

    1. Change identity_provider.id and related ForeignKeys to type integer.
    2. Create an unique constraint on users.password_hash.
    3. Drop unique constraint on users.email.
    """
    op.drop_constraint('fkey_identity_provider_user', 'users', type_='foreignkey')
    op.alter_column('users', 'identity_provider_id', type_=sa.Integer, postgresql_using="identity_provider_id::integer")
    op.alter_column('identity_providers', 'id', type_=sa.Integer, postgresql_using="id::integer")
    op.create_foreign_key('fkey_identity_provider_user', 'users', 'identity_providers', ['identity_provider_id'], ['id'])

    op.create_unique_constraint('users_password_hash_key', 'users', ['password_hash'])
    op.drop_constraint('users_email_key', 'users', type_='unique')
