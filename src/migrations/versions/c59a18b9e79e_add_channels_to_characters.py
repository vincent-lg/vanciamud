"""add_channels_to_characters

Revision ID: c59a18b9e79e
Revises: 2d61da0ff7ef
Create Date: 2022-04-29 12:54:40.809249

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c59a18b9e79e"
down_revision = "2d61da0ff7ef"
branch_labels = None
depends_on = None


def upgrade():
    """Add the channels column to the character table."""
    with op.batch_alter_table("character", schema=None) as batch_op:
        batch_op.add_column(sa.Column("channels", sa.Text(), nullable=True))


def downgrade():
    """Remove the channels column from the character table."""
    with op.batch_alter_table("character", schema=None) as batch_op:
        batch_op.drop_column("channels")
