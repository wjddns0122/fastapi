import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DailyTarot(Base):
    __tablename__ = "daily_tarots"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "relationship_id",
            "target_date",
            name="uq_daily_tarot_user_relationship_date",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("relationships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    question: Mapped[str] = mapped_column(String(200), nullable=False)
    card_name: Mapped[str] = mapped_column(String(50), nullable=False)
    card_orientation: Mapped[str] = mapped_column(String(20), nullable=False)
    ai_interpretation: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
