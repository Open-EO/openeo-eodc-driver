"""add roles and profiles

Revision ID: 17295e67b0c5
Revises: 030f4d30930d
Create Date: 2019-12-17 15:09:52.482662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17295e67b0c5'
down_revision = '030f4d30930d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'profiles',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('data_access', sa.Text, nullable=False),
    )
    op.add_column(
        'users',
        sa.Column('profile_id', sa.String, nullable=False)
    )
    op.create_foreign_key('fkey_profile_user', 'users', 'profiles', ['profile_id'], ['id'])


def downgrade():
    op.drop_constraint('fkey_profile_user', 'users', type_='foreignkey')
    op.drop_column('users', 'profile_id')
    op.drop_table('profiles')
