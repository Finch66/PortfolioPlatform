"""add asset metadata columns"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_asset_metadata"
down_revision = "0002_add_idempotency_key"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("transaction", sa.Column("asset_name", sa.String(), nullable=True))
    op.add_column("transaction", sa.Column("asset_type", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("transaction", "asset_type")
    op.drop_column("transaction", "asset_name")
