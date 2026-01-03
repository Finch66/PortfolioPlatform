"""create transactions table"""

from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transaction",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("operation_type", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("transaction")
