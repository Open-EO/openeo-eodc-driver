"""initial setup

Revision ID: 61d8d82e139b
Revises: 
Create Date: 2019-12-10 14:01:17.068940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61d8d82e139b'
down_revision = None
branch_labels = None
depends_on = None

auth_type = sa.Enum('basic', 'oidc', name='authtype')


def upgrade():
    op.create_table(
        'identity_providers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('issuer_url', sa.Text, nullable=False),
        sa.Column('scopes', sa.Text, nullable=False),
        sa.Column('title', sa.Text, nullable=False, unique=True),
        sa.Column('description', sa.Text),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('auth_type', auth_type, nullable=False),
        sa.Column('username', sa.Text),
        sa.Column('password_hash', sa.Text),
        sa.Column('email', sa.Text),
        sa.Column('identity_provider_id', sa.Integer),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    op.create_foreign_key('fkey_identity_provider_user', 'users', 'identity_providers', ['identity_provider_id'], ['id'])


def downgrade():
    op.drop_constraint('fkey_identity_provider_user', 'users', type_='foreignkey')
    op.drop_table('users')
    auth_type.drop(op.get_bind(), checkfirst=False)
    op.drop_table('identity_providers')
