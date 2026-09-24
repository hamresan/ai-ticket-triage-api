"""Create tickets table."""

from alembic import op
import sqlalchemy as sa

revision = "20260924_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("message", sa.String(length=10000), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(trim(subject)) > 0", name="ck_tickets_subject_not_blank"),
        sa.CheckConstraint("length(subject) <= 200", name="ck_tickets_subject_length"),
        sa.CheckConstraint("length(trim(message)) > 0", name="ck_tickets_message_not_blank"),
        sa.CheckConstraint("length(message) <= 10000", name="ck_tickets_message_length"),
        sa.CheckConstraint("status IN ('new', 'triaged', 'failed')", name="ck_tickets_status"),
        sa.CheckConstraint("updated_at >= created_at", name="ck_tickets_timestamps"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tickets")
