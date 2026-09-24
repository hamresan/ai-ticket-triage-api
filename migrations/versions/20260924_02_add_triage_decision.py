"""Add persisted triage decision fields."""

from alembic import op
import sqlalchemy as sa

revision = "20260924_02"
down_revision = "20260924_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("category", sa.String(length=32), nullable=True))
    op.add_column("tickets", sa.Column("priority", sa.String(length=16), nullable=True))
    op.add_column("tickets", sa.Column("sentiment", sa.String(length=16), nullable=True))
    op.add_column("tickets", sa.Column("needs_human_review", sa.Boolean(), nullable=True))
    op.add_column("tickets", sa.Column("suggested_reply", sa.String(length=4000), nullable=True))
    op.add_column("tickets", sa.Column("provenance", sa.String(length=16), nullable=True))
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.create_check_constraint(
            "ck_tickets_decision_state",
            "(status = 'triaged' AND category IS NOT NULL AND priority IS NOT NULL "
            "AND sentiment IS NOT NULL AND needs_human_review IS NOT NULL "
            "AND suggested_reply IS NOT NULL AND provenance IS NOT NULL) OR "
            "(status <> 'triaged' AND category IS NULL AND priority IS NULL "
            "AND sentiment IS NULL AND needs_human_review IS NULL "
            "AND suggested_reply IS NULL AND provenance IS NULL)",
        )


def downgrade() -> None:
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_constraint("ck_tickets_decision_state", type_="check")
        batch_op.drop_column("provenance")
        batch_op.drop_column("suggested_reply")
        batch_op.drop_column("needs_human_review")
        batch_op.drop_column("sentiment")
        batch_op.drop_column("priority")
        batch_op.drop_column("category")
