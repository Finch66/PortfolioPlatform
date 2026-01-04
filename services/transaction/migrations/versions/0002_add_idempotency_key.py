"""add idempotency_key column"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_idempotency_key"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transaction",
        sa.Column("idempotency_key", sa.String(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_transaction_idempotency_key",
        "transaction",
        ["idempotency_key"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_transaction_idempotency_key", "transaction", type_="unique")
    op.drop_column("transaction", "idempotency_key")
