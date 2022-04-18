"""add_room

Revision ID: 25b24442f732
Revises:
Create Date: 2022-04-17 18:11:57.195662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "25b24442f732"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add the room class and link to the character."""
    with op.batch_alter_table("character", schema=None) as batch_op:
        batch_op.add_column(sa.Column("room_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("room__index", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key("room_id", "room", ["room_id"], ["id"])


def downgrade():
    """Remove the link between character and room."""
    with op.batch_alter_table("character", schema=None) as batch_op:
        batch_op.drop_constraint("room_id", type_="foreignkey")
        batch_op.drop_column("room__index")
        batch_op.drop_column("room_id")
