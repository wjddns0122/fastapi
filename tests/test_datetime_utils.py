from datetime import UTC, datetime

from app.utils import datetime as datetime_utils


def test_get_seoul_today_falls_back_to_utc_when_timezone_data_missing(monkeypatch):
    class FakeZoneInfoNotFoundError(Exception):
        pass

    fixed_now = datetime(2026, 4, 10, 12, 30, tzinfo=UTC)

    class FakeDatetime:
        @staticmethod
        def now(tz):
            return fixed_now

    def raise_zoneinfo_not_found(_key):
        raise FakeZoneInfoNotFoundError

    monkeypatch.setattr(
        datetime_utils,
        "ZoneInfoNotFoundError",
        FakeZoneInfoNotFoundError,
    )
    monkeypatch.setattr(datetime_utils, "ZoneInfo", raise_zoneinfo_not_found)
    monkeypatch.setattr(datetime_utils, "datetime", FakeDatetime)

    assert datetime_utils.get_seoul_today() == fixed_now.date()
