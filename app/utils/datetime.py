from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_seoul_today() -> date:
    try:
        return datetime.now(ZoneInfo("Asia/Seoul")).date()
    except ZoneInfoNotFoundError:
        return datetime.now(UTC).date()
