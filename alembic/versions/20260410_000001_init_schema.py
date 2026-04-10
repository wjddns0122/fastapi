"""init schema

Revision ID: 20260410_000001
Revises:
Create Date: 2026-04-10 00:00:01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect  # upgrade()에서 기존 스키마 검사에 사용

# revision identifiers, used by Alembic.
revision = "20260410_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("nickname", sa.String(length=50), nullable=False),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.Column("profile_image_url", sa.String(length=500), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    if inspector.has_table("relationships"):
        relationship_columns = {
            column["name"]
            for column in inspector.get_columns("relationships")
        }
        if "base_score" not in relationship_columns:
            op.add_column("relationships", sa.Column("base_score", sa.Integer(), nullable=True))
    else:
        op.create_table(
            "relationships",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("requester_user_id", sa.String(length=36), nullable=False),
            sa.Column("target_user_id", sa.String(length=36), nullable=False),
            sa.Column("relationship_type", sa.String(length=20), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("base_score", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["requester_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["target_user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("requester_user_id", "target_user_id", name="uq_relationship_pair"),
        )
        op.create_index(
            op.f("ix_relationships_requester_user_id"),
            "relationships",
            ["requester_user_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_relationships_target_user_id"),
            "relationships",
            ["target_user_id"],
            unique=False,
        )

    inspector = inspect(bind)
    if not inspector.has_table("relationship_activities"):
        op.create_table(
            "relationship_activities",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("relationship_id", sa.String(length=36), nullable=False),
            sa.Column("actor_user_id", sa.String(length=36), nullable=False),
            sa.Column("event_type", sa.String(length=50), nullable=False),
            sa.Column("occurred_on", sa.Date(), nullable=False),
            sa.Column("metadata", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_relationship_activities_actor_user_id"),
            "relationship_activities",
            ["actor_user_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_relationship_activities_event_type"),
            "relationship_activities",
            ["event_type"],
            unique=False,
        )
        op.create_index(
            op.f("ix_relationship_activities_occurred_on"),
            "relationship_activities",
            ["occurred_on"],
            unique=False,
        )
        op.create_index(
            op.f("ix_relationship_activities_relationship_id"),
            "relationship_activities",
            ["relationship_id"],
            unique=False,
        )

    inspector = inspect(bind)
    if not inspector.has_table("daily_compatibilities"):
        op.create_table(
            "daily_compatibilities",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("relationship_id", sa.String(length=36), nullable=False),
            sa.Column("target_date", sa.Date(), nullable=False),
            sa.Column("base_score", sa.Integer(), nullable=False),
            sa.Column("tarot_score", sa.Integer(), nullable=False),
            sa.Column("behavior_score", sa.Integer(), nullable=False),
            sa.Column("final_score", sa.Integer(), nullable=False),
            sa.Column("summary", sa.String(length=255), nullable=False),
            sa.Column("prescription", sa.String(length=255), nullable=False),
            sa.Column("tarot_card_name", sa.String(length=50), nullable=False),
            sa.Column("tarot_orientation", sa.String(length=20), nullable=False),
            sa.Column("behavior_snapshot", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "relationship_id",
                "target_date",
                name="uq_daily_compatibility_relationship_date",
            ),
        )
        op.create_index(
            op.f("ix_daily_compatibilities_relationship_id"),
            "daily_compatibilities",
            ["relationship_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_daily_compatibilities_target_date"),
            "daily_compatibilities",
            ["target_date"],
            unique=False,
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_daily_compatibilities_target_date"), table_name="daily_compatibilities")
    op.drop_index(op.f("ix_daily_compatibilities_relationship_id"), table_name="daily_compatibilities")
    op.drop_table("daily_compatibilities")

    op.drop_index(op.f("ix_relationship_activities_relationship_id"), table_name="relationship_activities")
    op.drop_index(op.f("ix_relationship_activities_occurred_on"), table_name="relationship_activities")
    op.drop_index(op.f("ix_relationship_activities_event_type"), table_name="relationship_activities")
    op.drop_index(op.f("ix_relationship_activities_actor_user_id"), table_name="relationship_activities")
    op.drop_table("relationship_activities")

    op.drop_index(op.f("ix_relationships_target_user_id"), table_name="relationships")
    op.drop_index(op.f("ix_relationships_requester_user_id"), table_name="relationships")
    op.drop_table("relationships")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
