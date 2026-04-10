from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DailyCompatibility(Base):
    __tablename__ = "daily_compatibilities"
    __table_args__ = (
        UniqueConstraint("relationship_id", "target_date", name="uq_daily_compatibility_relationship_date"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    relationship_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("relationships.id"),
        nullable=False,
        index=True,
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    base_score: Mapped[int] = mapped_column(nullable=False)
    tarot_score: Mapped[int] = mapped_column(nullable=False)
    behavior_score: Mapped[int] = mapped_column(nullable=False)
    final_score: Mapped[int] = mapped_column(nullable=False)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    prescription: Mapped[str] = mapped_column(String(255), nullable=False)
    tarot_card_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tarot_orientation: Mapped[str] = mapped_column(String(20), nullable=False)
    behavior_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(UTC),
    )
