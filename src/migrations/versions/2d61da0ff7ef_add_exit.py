"""add_exit

Revision ID: 2d61da0ff7ef
Revises: 25b24442f732
Create Date: 2022-04-19 12:21:21.008302

"""

import pickle

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2d61da0ff7ef"
down_revision = "25b24442f732"
branch_labels = None
depends_on = None

ROOM_TABLE = sa.sql.table("room", sa.Column("exits", sa.LargeBinary()))


def upgrade():
    """Add the exits field to rooms."""
    # Add the column as nullable.
    with op.batch_alter_table("room", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("exits", sa.LargeBinary(), nullable=True)
        )

    # Add an empty dictionary as value for existing rows.
    op.execute(ROOM_TABLE.update().values({"exits": pickle.dumps({})}))


def downgrade():
    """Remove the exit field to rooms."""
    with op.batch_alter_table("room", schema=None) as batch_op:
        batch_op.drop_column("exits")
