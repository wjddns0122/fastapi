"""sync mvp gap schema

Revision ID: 20260515_000002
Revises: 20260410_000001
Create Date: 2026-05-15 00:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260515_000002"
down_revision = "20260410_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("daily_tarots"):
        op.create_table(
            "daily_tarots",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("relationship_id", sa.String(length=36), nullable=False),
            sa.Column("target_date", sa.Date(), nullable=False),
            sa.Column("question", sa.String(length=200), nullable=False),
            sa.Column("card_name", sa.String(length=50), nullable=False),
            sa.Column("card_orientation", sa.String(length=20), nullable=False),
            sa.Column("ai_interpretation", sa.String(length=500), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "user_id",
                "relationship_id",
                "target_date",
                name="uq_daily_tarot_user_relationship_date",
            ),
        )
        op.create_index(op.f("ix_daily_tarots_relationship_id"), "daily_tarots", ["relationship_id"])
        op.create_index(op.f("ix_daily_tarots_target_date"), "daily_tarots", ["target_date"])
        op.create_index(op.f("ix_daily_tarots_user_id"), "daily_tarots", ["user_id"])

    inspector = inspect(bind)
    if not inspector.has_table("letters"):
        op.create_table(
            "letters",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("relationship_id", sa.String(length=36), nullable=False),
            sa.Column("sender_user_id", sa.String(length=36), nullable=False),
            sa.Column("receiver_user_id", sa.String(length=36), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("letter_type", sa.String(length=20), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("condition_type", sa.String(length=50), nullable=True),
            sa.Column("scheduled_at", sa.DateTime(), nullable=True),
            sa.Column("sent_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["receiver_user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["sender_user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_letters_receiver_user_id"), "letters", ["receiver_user_id"])
        op.create_index(op.f("ix_letters_relationship_id"), "letters", ["relationship_id"])
        op.create_index(op.f("ix_letters_sender_user_id"), "letters", ["sender_user_id"])
    else:
        letter_columns = {column["name"] for column in inspector.get_columns("letters")}
        if "condition_type" not in letter_columns:
            op.add_column(
                "letters",
                sa.Column("condition_type", sa.String(length=50), nullable=True),
            )

    inspector = inspect(bind)
    if not inspector.has_table("mission_completions"):
        op.create_table(
            "mission_completions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("mission_id", sa.String(length=36), nullable=False),
            sa.Column("relationship_id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("target_date", sa.Date(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "mission_id",
                "relationship_id",
                "user_id",
                "target_date",
                name="uq_mission_completion_daily_user",
            ),
        )
        op.create_index(op.f("ix_mission_completions_mission_id"), "mission_completions", ["mission_id"])
        op.create_index(op.f("ix_mission_completions_relationship_id"), "mission_completions", ["relationship_id"])
        op.create_index(op.f("ix_mission_completions_target_date"), "mission_completions", ["target_date"])
        op.create_index(op.f("ix_mission_completions_user_id"), "mission_completions", ["user_id"])

    inspector = inspect(bind)
    if not inspector.has_table("weekly_reports"):
        op.create_table(
            "weekly_reports",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("relationship_id", sa.String(length=36), nullable=False),
            sa.Column("week_start", sa.Date(), nullable=False),
            sa.Column("week_end", sa.Date(), nullable=False),
            sa.Column("average_score", sa.Integer(), nullable=False),
            sa.Column("best_day", sa.Date(), nullable=True),
            sa.Column("worst_day", sa.Date(), nullable=True),
            sa.Column("summary", sa.String(length=500), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "relationship_id",
                "week_start",
                "week_end",
                name="uq_weekly_report_relationship_week",
            ),
        )
        op.create_index(op.f("ix_weekly_reports_relationship_id"), "weekly_reports", ["relationship_id"])
        op.create_index(op.f("ix_weekly_reports_week_end"), "weekly_reports", ["week_end"])
        op.create_index(op.f("ix_weekly_reports_week_start"), "weekly_reports", ["week_start"])

    inspector = inspect(bind)
    if not inspector.has_table("relationship_invitations"):
        op.create_table(
            "relationship_invitations",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("token", sa.String(length=64), nullable=False),
            sa.Column("requester_user_id", sa.String(length=36), nullable=False),
            sa.Column("relationship_type", sa.String(length=20), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("relationship_id", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["requester_user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_relationship_invitations_relationship_id"),
            "relationship_invitations",
            ["relationship_id"],
        )
        op.create_index(
            op.f("ix_relationship_invitations_requester_user_id"),
            "relationship_invitations",
            ["requester_user_id"],
        )
        op.create_index(
            op.f("ix_relationship_invitations_token"),
            "relationship_invitations",
            ["token"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table("relationship_invitations"):
        op.drop_index(op.f("ix_relationship_invitations_token"), table_name="relationship_invitations")
        op.drop_index(op.f("ix_relationship_invitations_requester_user_id"), table_name="relationship_invitations")
        op.drop_index(op.f("ix_relationship_invitations_relationship_id"), table_name="relationship_invitations")
        op.drop_table("relationship_invitations")

    inspector = inspect(bind)
    if inspector.has_table("weekly_reports"):
        op.drop_index(op.f("ix_weekly_reports_week_start"), table_name="weekly_reports")
        op.drop_index(op.f("ix_weekly_reports_week_end"), table_name="weekly_reports")
        op.drop_index(op.f("ix_weekly_reports_relationship_id"), table_name="weekly_reports")
        op.drop_table("weekly_reports")

    inspector = inspect(bind)
    if inspector.has_table("mission_completions"):
        op.drop_index(op.f("ix_mission_completions_user_id"), table_name="mission_completions")
        op.drop_index(op.f("ix_mission_completions_target_date"), table_name="mission_completions")
        op.drop_index(op.f("ix_mission_completions_relationship_id"), table_name="mission_completions")
        op.drop_index(op.f("ix_mission_completions_mission_id"), table_name="mission_completions")
        op.drop_table("mission_completions")

    inspector = inspect(bind)
    if inspector.has_table("letters"):
        letter_columns = {column["name"] for column in inspector.get_columns("letters")}
        if "condition_type" in letter_columns:
            with op.batch_alter_table("letters") as batch_op:
                batch_op.drop_column("condition_type")

    inspector = inspect(bind)
    if inspector.has_table("daily_tarots"):
        op.drop_index(op.f("ix_daily_tarots_user_id"), table_name="daily_tarots")
        op.drop_index(op.f("ix_daily_tarots_target_date"), table_name="daily_tarots")
        op.drop_index(op.f("ix_daily_tarots_relationship_id"), table_name="daily_tarots")
        op.drop_table("daily_tarots")
