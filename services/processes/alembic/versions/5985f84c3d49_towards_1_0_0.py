"""towards 1.0.0

Revision ID: 5985f84c3d49
Revises: b1a48c184bc4
Create Date: 2020-03-05 15:33:01.828090

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5985f84c3d49'
down_revision = 'b1a48c184bc4'
branch_labels = None
depends_on = None

data_type_enum = sa.Enum(
    'array',
    'boolean',
    'integer',
    'null',
    'number',
    'object',
    'string',
    name='data_type',
)


def upgrade():
    op.add_column('process_graphs', sa.Column('deprecated', sa.Boolean(), default=False, nullable=True))
    op.add_column('process_graphs', sa.Column('experimental', sa.Boolean(), default=False, nullable=True))
    op.add_column('process_graphs', sa.Column('examples', sa.JSON(), nullable=True))
    op.alter_column('process_graphs', 'title', new_column_name='summary')
    op.add_column('process_graphs', sa.Column('id_openeo', sa.String(), unique=True))
    process_graphs_id_openeo = sa.table('process_graphs', sa.column('id_openeo'))
    op.execute(process_graphs_id_openeo.update().values(id_openeo=sa.column('id')))

    op.create_table(
        'parameter',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey('process_graphs.id')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=False),
        sa.Column('optional', sa.Boolean(), default=False, nullable=True),
        sa.Column('deprecated', sa.Boolean(), default=False, nullable=True),
        sa.Column('experimental', sa.Boolean(), default=False, nullable=True),
        sa.Column('default', sa.TEXT(), nullable=True),
    )
    op.create_foreign_key('parameter_process_graph_fkey', 'parameter', 'process_graphs', ['process_graph_id'], ['id'])
    op.create_table(
        'return',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey('process_graphs.id')),
        sa.Column('description', sa.TEXT(), nullable=True),
    )
    op.create_foreign_key('return_process_graph_fkey', 'return', 'process_graphs', ['process_graph_id'], ['id'])
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey('process_graphs.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
    )
    op.create_foreign_key('category_process_graph_fkey', 'category', 'process_graphs', ['process_graph_id'], ['id'])
    op.create_table(
        'schema',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('parameter_id', sa.Integer(), sa.ForeignKey('parameter.id'), nullable=True),
        sa.Column('return_id', sa.Integer(), sa.ForeignKey('return.id'), nullable=True),
        sa.Column('schema_id', sa.Integer(), sa.ForeignKey('schema.id'), nullable=True),
        sa.Column('subtype', sa.String(), nullable=True),
        sa.Column('pattern', sa.String(), nullable=True),
        sa.Column('minimum', sa.Float(), nullable=True),
        sa.Column('maximum', sa.Float(), nullable=True),
        sa.Column('min_items', sa.Float(), nullable=True),
        sa.Column('max_items', sa.Float(), nullable=True),
    )
    op.create_check_constraint('check_min_items_positive', 'schema', sa.sql.column('min_items') >= 0)
    op.create_check_constraint('check_max_items_positive', 'schema', sa.sql.column('max_items') >= 0)
    # needs to be added after schema table is created
    op.add_column(
        'parameter',
        sa.Column('schema_id', sa.Integer(), sa.ForeignKey('schema.id'), nullable=True),
    )
    op.create_foreign_key('parameter_schema_fkey', 'parameter', 'schema', ['schema_id'], ['id'])
    op.create_foreign_key('schema_parameter_fkey', 'schema', 'parameter', ['parameter_id'], ['id'])
    op.create_foreign_key('schema_return_fkey', 'schema', 'return', ['return_id'], ['id'])
    op.create_table(
        'schema_type',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('schema_id', sa.Integer(), sa.ForeignKey('schema.id'), nullable=False),
        sa.Column('name', data_type_enum, nullable=False),
    )
    op.create_foreign_key('schema_type_schema_fkey', 'schema_type', 'schema', ['schema_id'], ['id'])
    op.create_table(
        'schema_enum',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('schema_id', sa.Integer(), sa.ForeignKey('schema.id'), nullable=False),
        sa.Column('name', sa.TEXT(), nullable=False),
    )
    op.create_foreign_key('schema_enum_schema_fkey', 'schema_enum', 'schema', ['schema_id'], ['id'])
    op.create_table(
        'exception',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey('process_graphs.id')),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('message', sa.TEXT(), nullable=False),
        sa.Column('http', sa.Integer(), default=400),
        sa.Column('error_code', sa.String(), nullable=False),
    )
    op.create_foreign_key('exception_process_graph_fkey', 'exception', 'process_graphs', ['process_graph_id'], ['id'])
    op.create_table(
        'link',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.String(), sa.ForeignKey('process_graphs.id')),
        sa.Column('rel', sa.String(), nullable=False),
        sa.Column('href', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
    )
    op.create_foreign_key('link_process_graph_fkey', 'link', 'process_graphs', ['process_graph_id'], ['id'])


def downgrade():
    op.drop_constraint('schema_enum_schema_fkey', 'schema_enum', type_='foreignkey')
    op.drop_constraint('schema_type_schema_fkey', 'schema_type', type_='foreignkey')
    op.drop_constraint('schema_return_fkey', 'schema', type_='foreignkey')
    op.drop_constraint('schema_parameter_fkey', 'schema', type_='foreignkey')
    op.drop_constraint('parameter_schema_fkey', 'parameter', type_='foreignkey')
    op.drop_constraint('parameter_schema_id_fkey', 'parameter', type_='foreignkey')
    op.drop_constraint('category_process_graph_fkey', 'category', type_='foreignkey')
    op.drop_constraint('return_process_graph_fkey', 'return', type_='foreignkey')
    op.drop_constraint('parameter_process_graph_fkey', 'parameter', type_='foreignkey')
    op.drop_constraint('exception_process_graph_fkey', 'exception', type_='foreignkey')
    op.drop_constraint('link_process_graph_fkey', 'link', type_='foreignkey')

    op.drop_constraint('check_min_items_positive', 'schema', type_='check')
    op.drop_constraint('check_max_items_positive', 'schema', type_='check')

    op.drop_table('link')
    op.drop_table('exception')
    op.drop_table('schema_enum')
    op.drop_table('schema_type')
    op.drop_table('schema')
    op.drop_table('category')
    op.drop_table('return')
    op.drop_table('parameter')

    data_type_enum.drop(op.get_bind(), checkfirst=False)

    op.drop_column('process_graphs', 'deprecated')
    op.drop_column('process_graphs', 'experimental')
    op.drop_column('process_graphs', 'examples')
    op.alter_column('process_graphs', 'summary', new_column_name='title')
    op.drop_column('process_graphs', 'id_openeo')
