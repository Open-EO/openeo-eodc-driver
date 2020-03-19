"""merge predefined process

Revision ID: 66a28397b413
Revises: 5985f84c3d49
Create Date: 2020-03-17 15:37:56.857734

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '66a28397b413'
down_revision = '5985f84c3d49'
branch_labels = None
depends_on = None


process_definition_enum = sa.Enum(
    'predefined',
    'user_defined',
    name='process_definition',
)


def upgrade():
    process_definition_enum.create(op.get_bind(), checkfirst=False)
    op.add_column('process_graphs', sa.Column('process_definition', process_definition_enum))
    process_definition = sa.table('process_graphs', sa.column('process_definition'))
    op.execute(process_definition.update().values(process_definition='user_defined'))
    op.alter_column('process_graphs', 'process_definition', nullable=True)

    op.alter_column('process_graphs', 'user_id', nullable=True)


def downgrade():
    process_graph_user_id = sa.table('process_graphs', sa.column('user_id'))

    op.execute(process_graph_user_id.update().values(user_id='default-user'))
    op.alter_column('process_graphs', 'user_id', nullable=False)
    op.drop_column('process_graphs', 'process_definition')
    process_definition_enum.drop(op.get_bind(), checkfirst=False)
