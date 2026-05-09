from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo


def get_seoul_today() -> date:
    return datetime.now(ZoneInfo("Asia/Seoul")).date()
