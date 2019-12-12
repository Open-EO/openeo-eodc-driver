"""Correct users id type

Revision ID: 1efc54cd3649
Revises: 61d8d82e139b
Create Date: 2019-12-11 13:51:01.593867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1efc54cd3649'
down_revision = '61d8d82e139b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('users', 'id')
    op.add_column('users',
        sa.Column('id', sa.String(), nullable=False, unique=True)
    )
    op.drop_column('users', 'username')
    op.add_column('users',
        sa.Column('username', sa.Text(), nullable=False, unique=True)
    )
    op.drop_column('users', 'password_hash')
    op.add_column('users',
        sa.Column('password_hash', sa.Text(), nullable=False, unique=True)
    )


def downgrade():
    op.drop_column('users', 'id')
    op.add_column('users',
        sa.Column('id', sa.Integer(), nullable=False)
    )
    op.drop_column('users', 'username')
    op.add_column('users',
        sa.Column('username', sa.Integer(), nullable=False)
    )
    op.drop_column('users', 'password_hash')
    op.add_column('users',
        sa.Column('password_hash', sa.Integer(), nullable=False)
    )
