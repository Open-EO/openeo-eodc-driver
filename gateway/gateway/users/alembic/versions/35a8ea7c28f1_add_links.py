"""add links

Revision ID: 35a8ea7c28f1
Revises: 943d0bb2c339
Create Date: 2020-03-18 12:54:00.965100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35a8ea7c28f1'
down_revision = '943d0bb2c339'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'links',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('identity_provider_id', sa.String(), sa.ForeignKey('identity_providers.id')),
        sa.Column('rel', sa.String(), nullable=False),
        sa.Column('href', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
    )


def downgrade():
    op.drop_table('links')
