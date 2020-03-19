"""update users

Revision ID: 06082d6cce6b
Revises: 35a8ea7c28f1
Create Date: 2020-03-19 12:11:04.463553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06082d6cce6b'
down_revision = '35a8ea7c28f1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('budget', sa.Integer()))
    op.create_table(
        'storage',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('free', sa.Integer(), nullable=False),
        sa.Column('quota', sa.Integer(), nullable=False),
    )
    op.create_foreign_key('storage_user_fkey', 'storage', 'users', ['user_id'], ['id'])
    op.add_column('links', sa.Column('user_id', sa.String(), sa.ForeignKey('users.id')))
    op.create_foreign_key('link_user_fkey', 'links', 'users', ['user_id'], ['id'])


def downgrade():
    op.drop_constraint('link_user_fkey', 'links', type_='foreignkey')
    op.drop_column('links', 'user_id')
    op.drop_constraint('storage_user_fkey', 'storage', type_='foreignkey')
    op.drop_table('storage')
    op.drop_column('users', 'budget')
