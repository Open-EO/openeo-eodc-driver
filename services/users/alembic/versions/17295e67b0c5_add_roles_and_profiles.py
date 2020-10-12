"""add roles and profiles.

Revision ID: 17295e67b0c5
Revises: 030f4d30930d
Create Date: 2019-12-17 15:09:52.482662
"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '17295e67b0c5'
down_revision = '030f4d30930d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade DB model.

    Create table profiles and a relationship to users - to connect a user with data_access rights.
    """
    op.create_table(
        'profiles',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('name', sa.Text, nullable=False, unique=True),
        sa.Column('data_access', sa.Text, nullable=False),
    )
    op.add_column('users', sa.Column('profile_id', sa.String, nullable=False))
    op.create_foreign_key('fkey_profile_user', 'users', 'profiles', ['profile_id'], ['id'])


def downgrade() -> None:
    """Downgrade DB model.

    Drop table profiles with relations.
    """
    op.drop_constraint('fkey_profile_user', 'users', type_='foreignkey')
    op.drop_column('users', 'profile_id')
    op.drop_table('profiles')
