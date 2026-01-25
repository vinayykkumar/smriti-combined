"""
Unit tests for sunrise calculation utilities.

Tests day_key generation and sunrise times for different timezones.
"""

import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.quotes.sunrise import (
    get_sunrise_info_for_user,
    get_day_key_for_user,
    get_coordinates_for_timezone,
    get_sunrise_times,
)
from app.quotes.constants import DEFAULT_TIMEZONE


class TestGetCoordinatesForTimezone:
    """Test timezone to coordinates mapping."""

    def test_known_timezone_returns_coordinates(self):
        """Known timezones should return their representative coordinates."""
        lat, lng = get_coordinates_for_timezone("America/New_York")
        assert lat == pytest.approx(40.7128, rel=0.01)
        assert lng == pytest.approx(-74.0060, rel=0.01)

    def test_asia_kolkata_coordinates(self):
        """Test Asia/Kolkata timezone coordinates."""
        lat, lng = get_coordinates_for_timezone("Asia/Kolkata")
        assert lat == pytest.approx(28.6139, rel=0.01)
        assert lng == pytest.approx(77.2090, rel=0.01)

    def test_unknown_timezone_returns_default(self):
        """Unknown timezones should return default coordinates."""
        lat, lng = get_coordinates_for_timezone("Unknown/Timezone")
        assert lat == 0.0
        assert lng == 0.0


class TestGetSunriseTimes:
    """Test sunrise calculation for specific locations."""

    def test_new_york_sunrise_reasonable_time(self):
        """New York sunrise should be between 5 AM and 8 AM local time."""
        from datetime import date

        today_sunrise, tomorrow_sunrise = get_sunrise_times(
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
            for_date=date(2026, 1, 25)
        )

        # Convert to local time for checking
        tz = ZoneInfo("America/New_York")
        local_sunrise = today_sunrise.astimezone(tz)

        # In January, NYC sunrise is around 7:10 AM
        assert 5 <= local_sunrise.hour <= 8

    def test_kolkata_sunrise_reasonable_time(self):
        """Kolkata sunrise should be between 5 AM and 7 AM local time."""
        from datetime import date

        today_sunrise, tomorrow_sunrise = get_sunrise_times(
            latitude=28.6139,
            longitude=77.2090,
            timezone="Asia/Kolkata",
            for_date=date(2026, 1, 25)
        )

        # Convert to local time
        tz = ZoneInfo("Asia/Kolkata")
        local_sunrise = today_sunrise.astimezone(tz)

        # In January, Delhi sunrise is around 7:00 AM
        assert 5 <= local_sunrise.hour <= 8

    def test_tomorrow_sunrise_is_after_today(self):
        """Tomorrow's sunrise should be approximately 24 hours after today's."""
        from datetime import date

        today_sunrise, tomorrow_sunrise = get_sunrise_times(
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
            for_date=date(2026, 1, 25)
        )

        diff = tomorrow_sunrise - today_sunrise
        # Should be close to 24 hours (within a few minutes due to day length changes)
        assert 23.5 <= diff.total_seconds() / 3600 <= 24.5


class TestGetDayKeyForUser:
    """Test day_key generation for different scenarios."""

    def test_after_sunrise_returns_today(self):
        """Time after sunrise should return today's date as day_key."""
        # 3 PM UTC on Jan 25, 2026 - after sunrise everywhere
        reference = datetime(2026, 1, 25, 15, 0, 0, tzinfo=ZoneInfo("UTC"))

        day_key = get_day_key_for_user(
            user_timezone="America/New_York",
            user_latitude=40.7128,
            user_longitude=-74.0060,
            reference_time=reference
        )

        # 3 PM UTC = 10 AM EST, which is after sunrise (~7:10 AM EST in January)
        assert day_key == "2026-01-25"

    def test_before_sunrise_returns_yesterday(self):
        """Time before sunrise should return yesterday's date as day_key."""
        # 10 AM UTC = 5 AM EST (before sunrise in NYC)
        reference = datetime(2026, 1, 25, 10, 0, 0, tzinfo=ZoneInfo("UTC"))

        day_key = get_day_key_for_user(
            user_timezone="America/New_York",
            user_latitude=40.7128,
            user_longitude=-74.0060,
            reference_time=reference
        )

        # 5 AM EST is before sunrise, so still in Jan 24's "day"
        assert day_key == "2026-01-24"

    def test_kolkata_afternoon_returns_same_day(self):
        """Afternoon in Kolkata should return the same calendar date."""
        # 9 AM UTC = 2:30 PM IST (well after sunrise)
        reference = datetime(2026, 1, 25, 9, 0, 0, tzinfo=ZoneInfo("UTC"))

        day_key = get_day_key_for_user(
            user_timezone="Asia/Kolkata",
            user_latitude=28.6139,
            user_longitude=77.2090,
            reference_time=reference
        )

        assert day_key == "2026-01-25"

    def test_kolkata_early_morning_returns_yesterday(self):
        """Early morning in Kolkata (before sunrise) should return yesterday."""
        # 0:30 AM UTC = 6:00 AM IST (before sunrise ~7 AM)
        reference = datetime(2026, 1, 25, 0, 30, 0, tzinfo=ZoneInfo("UTC"))

        day_key = get_day_key_for_user(
            user_timezone="Asia/Kolkata",
            user_latitude=28.6139,
            user_longitude=77.2090,
            reference_time=reference
        )

        assert day_key == "2026-01-24"

    def test_default_timezone_when_none_provided(self):
        """Should use DEFAULT_TIMEZONE when no timezone provided."""
        reference = datetime(2026, 1, 25, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

        day_key = get_day_key_for_user(
            user_timezone=None,
            user_latitude=None,
            user_longitude=None,
            reference_time=reference
        )

        # Should use UTC and default coordinates (equator)
        assert day_key == "2026-01-25"

    def test_timezone_without_coordinates_uses_representative(self):
        """Should use representative coordinates for timezone when none provided."""
        reference = datetime(2026, 1, 25, 15, 0, 0, tzinfo=ZoneInfo("UTC"))

        day_key = get_day_key_for_user(
            user_timezone="America/New_York",
            user_latitude=None,
            user_longitude=None,
            reference_time=reference
        )

        # Should still work using NYC representative coordinates
        assert day_key == "2026-01-25"


class TestGetSunriseInfoForUser:
    """Test full sunrise info retrieval."""

    def test_returns_all_required_fields(self):
        """Should return all required fields."""
        reference = datetime(2026, 1, 25, 15, 0, 0, tzinfo=ZoneInfo("UTC"))

        info = get_sunrise_info_for_user(
            user_timezone="America/New_York",
            user_latitude=40.7128,
            user_longitude=-74.0060,
            reference_time=reference
        )

        assert "day_key" in info
        assert "day_sunrise_utc" in info
        assert "next_sunrise_utc" in info
        assert "timezone" in info

        assert info["timezone"] == "America/New_York"
        assert isinstance(info["day_sunrise_utc"], datetime)
        assert isinstance(info["next_sunrise_utc"], datetime)

    def test_next_sunrise_after_day_sunrise(self):
        """next_sunrise_utc should always be after day_sunrise_utc."""
        reference = datetime(2026, 1, 25, 15, 0, 0, tzinfo=ZoneInfo("UTC"))

        info = get_sunrise_info_for_user(
            user_timezone="Asia/Kolkata",
            reference_time=reference
        )

        assert info["next_sunrise_utc"] > info["day_sunrise_utc"]

    def test_reference_time_between_sunrises(self):
        """Reference time should be between day_sunrise and next_sunrise."""
        reference = datetime(2026, 1, 25, 15, 0, 0, tzinfo=ZoneInfo("UTC"))

        info = get_sunrise_info_for_user(
            user_timezone="America/New_York",
            user_latitude=40.7128,
            user_longitude=-74.0060,
            reference_time=reference
        )

        # Reference time should be within the current "day"
        assert info["day_sunrise_utc"] <= reference < info["next_sunrise_utc"]
