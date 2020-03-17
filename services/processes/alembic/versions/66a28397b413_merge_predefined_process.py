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
    op.alter_column('parameter', 'process_graph_id', nullable=True)
    op.alter_column('return', 'process_graph_id', nullable=True)

    op.alter_column('link', 'type', nullable=True)
    op.alter_column('link', 'title', nullable=True)

    op.alter_column('exception', 'error_code', type_=sa.String())

    process_definition_enum.create(op.get_bind(), checkfirst=False)
    op.add_column('process_graph', sa.Column('process_definition', process_definition_enum))
    process_definition = sa.table('process_graph', sa.column('process_definition'))
    op.execute(process_definition.update().values(process_definition='predefined'))
    op.alter_column('process_graph', 'process_definition', nullable=True)
    op.alter_column('process_graph', 'user_id', nullable=True)


def downgrade():
    op.alter_column('process_graph', 'user_id', nullable=False)
    op.drop_column('process_graph', 'process_definition')
    process_definition_enum.drop(op.get_bind(), checkfirst=False)

    # Only works if error_code columns contain only valid integers
    op.alter_column('exception', 'error_code', type_=sa.Integer(), postgresql_using='error_code::integer')

    link_type = sa.table('link', sa.column('type'))
    op.execute(link_type.update().values(type=''))
    op.alter_column('link', 'type', nullable=False)
    link_title = sa.table('link', sa.column('title'))
    op.execute(link_title.update().values(title=''))
    op.alter_column('link', 'title', nullable=False)

    # Only works on empty table
    op.alter_column('parameter', 'process_graph_id', nullable=True)
    op.alter_column('return', 'process_graph_id', nullable=True)
