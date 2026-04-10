from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def get_seoul_today():
    return datetime.now(ZoneInfo("Asia/Seoul")).date()
