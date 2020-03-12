"""towards 1.0.0

Revision ID: 5985f84c3d49
Revises: b1a48c184bc4
Create Date: 2020-03-05 15:33:01.828090

"""
from uuid import uuid4

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

    op.drop_table('process_graphs')
    op.create_table(
        'process_graph',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('openeo_id', sa.String(), unique=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('deprecated', sa.Boolean(), default=False, nullable=True),
        sa.Column('experimental', sa.Boolean(), default=False, nullable=True),
        sa.Column('process_graph', sa.JSON(), default={}),
        sa.Column('examples', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_table(
        'parameter',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.Integer(), sa.ForeignKey('process_graph.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=False),
        sa.Column('optional', sa.Boolean(), default=False, nullable=True),
        sa.Column('deprecated', sa.Boolean(), default=False, nullable=True),
        sa.Column('experimental', sa.Boolean(), default=False, nullable=True),
        sa.Column('default', sa.TEXT(), nullable=True),
    )
    op.create_foreign_key('parameter_process_graph_fkey', 'parameter', 'process_graph', ['process_graph_id'], ['id'])
    op.create_table(
        'return',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.Integer(), sa.ForeignKey('process_graph.id'), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
    )
    op.create_foreign_key('return_process_graph_fkey', 'return', 'process_graph', ['process_graph_id'], ['id'])
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.Integer(), sa.ForeignKey('process_graph.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
    )
    op.create_foreign_key('category_process_graph_fkey', 'category', 'process_graph', ['process_graph_id'], ['id'])
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
        sa.Column('process_graph_id', sa.Integer(), sa.ForeignKey('process_graph.id')),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('message', sa.TEXT(), nullable=False),
        sa.Column('http', sa.Integer(), default=400),
        sa.Column('error_code', sa.Integer(), nullable=False),
    )
    op.create_foreign_key('exception_process_graph_fkey', 'exception', 'process_graph', ['process_graph_id'], ['id'])
    op.create_table(
        'link',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_graph_id', sa.Integer(), sa.ForeignKey('process_graph.id')),
        sa.Column('rel', sa.String(), nullable=False),
        sa.Column('href', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
    )
    op.create_foreign_key('link_process_graph_fkey', 'link', 'process_graph', ['process_graph_id'], ['id'])


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
    op.drop_table('process_graph')

    data_type_enum.drop(op.get_bind(), checkfirst=False)

    op.create_table(
        'process_graphs',
        sa.Column('id', sa.String()),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('process_graph', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
