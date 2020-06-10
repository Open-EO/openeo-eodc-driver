"""separate example

Revision ID: e773c1a9c7f9
Revises: 66a28397b413
Create Date: 2020-03-17 18:31:00.819754

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e773c1a9c7f9'
down_revision = '66a28397b413'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'example',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey('process_graphs.id'), nullable=False),
        sa.Column('process_graph', sa.JSON(), nullable=True),
        sa.Column('arguments', sa.JSON(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('returns', sa.String(), nullable=True),
        sa.Column('return_type', sa.String(), nullable=True),
    )
    op.create_foreign_key('example_process_graph_fkey', 'example', 'process_graphs', ['process_graph_id'], ['id'])
    op.create_check_constraint('check_process_graph_or_arguments', 'example',
                               'process_graph' != None or 'arguments' != None)

    op.add_column('parameter', sa.Column('default_type', sa.String(), nullable=True))
    op.add_column('schema', sa.Column('additional', sa.JSON(), nullable=True))
    op.add_column('schema', sa.Column('items', sa.JSON(), nullable=True))
    op.drop_constraint('schema_schema_id_fkey', 'schema', type_='foreignkey')
    op.drop_column('schema', 'schema_id')


def downgrade():
    op.add_column('schema', sa.Column('schema_id', sa.Integer(), sa.ForeignKey('schema.id'), nullable=True))
    op.drop_column('schema', 'items')
    op.drop_column('schema', 'additional')
    op.drop_column('parameter', 'default_type')

    op.drop_constraint('check_process_graph_or_arguments', 'example', type_='check')
    op.drop_constraint('example_process_graph_fkey', 'example', type_='foreignkey')
    op.drop_table('example')
