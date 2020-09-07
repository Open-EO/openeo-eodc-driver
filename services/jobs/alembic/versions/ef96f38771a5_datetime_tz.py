"""datetime-TZ

Revision ID: ef96f38771a5
Revises: 39785729dd56
Create Date: 2020-08-26 21:24:32.005844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef96f38771a5'
down_revision = '39785729dd56'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('jobs', 'created_at', type_=sa.DateTime(timezone=True), nullable=False)
    op.alter_column('jobs', 'updated_at', type_=sa.DateTime(timezone=True), nullable=False)
    op.alter_column('jobs', 'status_updated_at', type_=sa.DateTime(timezone=True), nullable=False)


def downgrade():
    op.alter_column('jobs', 'created_at', type_=sa.DateTime(), nullable=False)
    op.alter_column('jobs', 'updated_at', type_=sa.DateTime(), nullable=False)
    op.alter_column('jobs', 'status_updated_at', type_=sa.DateTime(), nullable=False)
