"""change process graph ids

Revision ID: b307ddba1c74
Revises: e773c1a9c7f9
Create Date: 2020-03-19 16:09:48.870100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b307ddba1c74'
down_revision = 'e773c1a9c7f9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('process_graphs', sa.Column('id_openeo_new', sa.String()))
    tab = sa.table('process_graphs', sa.Column('id_openeo_new'))
    op.execute(tab.update().values(id_openeo_new=sa.column('id_openeo')))
    op.drop_column('process_graphs', 'id_openeo')
    op.alter_column('process_graphs', 'id_openeo_new', new_column_name='id_openeo', nullable=False)
    op.create_unique_constraint('uq_process_graph_user_id', 'process_graphs', ['user_id', 'id_openeo'])


def downgrade():
    op.drop_constraint('uq_process_graph_user_id', 'process_graphs', type_='unique')
    op.add_column('process_graphs', sa.Column('id_openeo_new', sa.String()))
    tab = sa.table('process_graphs', sa.Column('id_openeo_new'))
    op.execute(tab.update().values(id_openeo_new=sa.column('id_openeo')))
    op.drop_column('process_graphs', 'id_openeo')
    op.alter_column('process_graphs', 'id_openeo_new', new_column_name='id_openeo')
    op.create_unique_constraint('uq_process_graph_id', 'process_graphs', ['id_openeo'])
