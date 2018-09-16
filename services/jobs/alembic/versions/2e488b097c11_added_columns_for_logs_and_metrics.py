"""Added columns for logs and metrics

Revision ID: 2e488b097c11
Revises: df179cb24786
Create Date: 2018-09-07 18:30:41.050806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e488b097c11'
down_revision = 'df179cb24786'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('jobs',
        sa.Column('logs', sa.String(), nullable=True)
    )
    op.add_column('jobs',
        sa.Column('metrics', sa.JSON(), nullable=True)
    )


def downgrade():
    op.drop_column('jobs', 'logs')
    op.drop_column('jobs', 'metrics')
