"""Add caller-supplied ticket idempotency records."""

from alembic import op
import sqlalchemy as sa

revision = "20260925_03"
down_revision = "20260924_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ticket_idempotency",
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("ticket_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("key"),
        sa.UniqueConstraint("ticket_id", name="uq_ticket_idempotency_ticket_id"),
    )


def downgrade() -> None:
    op.drop_table("ticket_idempotency")
