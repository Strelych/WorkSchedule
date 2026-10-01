"""Initial scheduler schema

Revision ID: 20260929_init
Revises: 
Create Date: 2026-09-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260929_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("admin", "supervisor", "valet_day", "valet_night", name="userrole"), nullable=False),
        sa.Column("status", sa.Enum("pending", "active", "blocked", name="userstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
    )
    op.create_table(
        "planning_periods",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("draft", "open", "closed", name="planningperiodstatus"), nullable=False),
        sa.Column("created_by", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "shift_slots",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("period_id", sa.String(length=36), sa.ForeignKey("planning_periods.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("shift_type_id", sa.String(length=64), nullable=False),
        sa.Column("role_required", sa.String(length=32), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("duration_hours", sa.Integer(), nullable=False),
        sa.Column("max_people", sa.Integer(), nullable=False),
        sa.Column("current_people", sa.Integer(), nullable=False),
        sa.Column("is_overnight", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "assignments",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("slot_id", sa.String(length=36), sa.ForeignKey("shift_slots.id"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Enum("draft", "submitted", "approved", "cancelled", name="assignmentstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "swap_requests",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("assignment_id", sa.String(length=36), sa.ForeignKey("assignments.id"), nullable=False),
        sa.Column("from_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("to_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.Enum("pending", "pending_approval", "approved", "rejected", name="swapstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("swap_requests")
    op.drop_table("assignments")
    op.drop_table("shift_slots")
    op.drop_table("planning_periods")
    op.drop_table("users")
