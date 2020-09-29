"""remove pg from examples

Revision ID: f970bc0608e5
Revises: b307ddba1c74
Create Date: 2020-09-24 15:45:39.207147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f970bc0608e5'
down_revision = 'b307ddba1c74'
branch_labels = None
depends_on = None


def upgrade():
    # see https://github.com/Open-EO/openeo-api/blob/master/CHANGELOG.md#removed
    op.drop_constraint('check_process_graph_or_arguments', 'example', type_='check')
    op.drop_column("example", "process_graph")
    op.execute("UPDATE example SET arguments = '{}'::json WHERE arguments IS NULL;")
    op.alter_column("example", "arguments", nullable=False)


def downgrade():
    op.alter_column("example", "arguments", nullable=True)
    op.add_column("example", sa.Column("process_graph", sa.JSON(), nullable=True))
    op.create_check_constraint('check_process_graph_or_arguments', 'example',
                               'process_graph' != None or 'arguments' != None)
