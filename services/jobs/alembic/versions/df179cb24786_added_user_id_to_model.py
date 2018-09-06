"""Added user_id to model

Revision ID: df179cb24786
Revises: 9e0975c7737a
Create Date: 2018-09-03 15:44:36.410626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df179cb24786'
down_revision = '9e0975c7737a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('jobs',
        sa.Column('user_id', sa.String(), nullable=False)
    )


def downgrade():
    op.drop_column('jobs', 'user_id')
