"""
Sunrise calculation utilities for the Today's Quote feature.

Uses the astral library to calculate accurate sunrise times based on
user's latitude, longitude, and timezone.
"""

from datetime import datetime, timedelta, date
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

from astral import LocationInfo
from astral.sun import sun

from app.quotes.constants import (
    DEFAULT_TIMEZONE,
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
)


# Representative coordinates for common timezones when user has no location
# These are approximate city centers that represent the timezone well
TIMEZONE_COORDINATES = {
    # Americas
    "America/New_York": (40.7128, -74.0060),      # New York City
    "America/Chicago": (41.8781, -87.6298),        # Chicago
    "America/Denver": (39.7392, -104.9903),        # Denver
    "America/Los_Angeles": (34.0522, -118.2437),   # Los Angeles
    "America/Toronto": (43.6532, -79.3832),        # Toronto
    "America/Vancouver": (49.2827, -123.1207),     # Vancouver
    "America/Mexico_City": (19.4326, -99.1332),    # Mexico City
    "America/Sao_Paulo": (-23.5505, -46.6333),     # Sao Paulo

    # Europe
    "Europe/London": (51.5074, -0.1278),           # London
    "Europe/Paris": (48.8566, 2.3522),             # Paris
    "Europe/Berlin": (52.5200, 13.4050),           # Berlin
    "Europe/Moscow": (55.7558, 37.6173),           # Moscow

    # Asia
    "Asia/Kolkata": (28.6139, 77.2090),            # New Delhi (for IST)
    "Asia/Mumbai": (19.0760, 72.8777),             # Mumbai
    "Asia/Tokyo": (35.6762, 139.6503),             # Tokyo
    "Asia/Shanghai": (31.2304, 121.4737),          # Shanghai
    "Asia/Singapore": (1.3521, 103.8198),          # Singapore
    "Asia/Dubai": (25.2048, 55.2708),              # Dubai
    "Asia/Hong_Kong": (22.3193, 114.1694),         # Hong Kong

    # Oceania
    "Australia/Sydney": (-33.8688, 151.2093),      # Sydney
    "Australia/Melbourne": (-37.8136, 144.9631),   # Melbourne
    "Pacific/Auckland": (-36.8485, 174.7633),      # Auckland

    # Africa
    "Africa/Johannesburg": (-26.2041, 28.0473),    # Johannesburg
    "Africa/Cairo": (30.0444, 31.2357),            # Cairo

    # Default (equator at prime meridian - sunrise ~6 AM year-round)
    "UTC": (0.0, 0.0),
}


def get_coordinates_for_timezone(timezone: str) -> Tuple[float, float]:
    """
    Get representative coordinates for a timezone.

    Falls back to default coordinates if timezone not in mapping.

    Args:
        timezone: IANA timezone string

    Returns:
        Tuple of (latitude, longitude)
    """
    return TIMEZONE_COORDINATES.get(timezone, (DEFAULT_LATITUDE, DEFAULT_LONGITUDE))


def get_sunrise_times(
    latitude: float,
    longitude: float,
    timezone: str,
    for_date: date
) -> Tuple[datetime, datetime]:
    """
    Calculate sunrise for a given date and the next day's sunrise.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        timezone: IANA timezone string
        for_date: The date to calculate sunrise for

    Returns:
        Tuple of (today_sunrise_utc, tomorrow_sunrise_utc)

    Raises:
        ValueError: If sunrise cannot be calculated (polar regions)
    """
    tz = ZoneInfo(timezone)
    utc = ZoneInfo("UTC")

    location = LocationInfo(
        name="user_location",
        region="",
        timezone=timezone,
        latitude=latitude,
        longitude=longitude
    )

    try:
        today_sun = sun(location.observer, date=for_date, tzinfo=tz)
        tomorrow_sun = sun(location.observer, date=for_date + timedelta(days=1), tzinfo=tz)

        today_sunrise = today_sun["sunrise"].astimezone(utc)
        tomorrow_sunrise = tomorrow_sun["sunrise"].astimezone(utc)

    except ValueError:
        # Polar regions - sun doesn't rise/set
        # Fall back to 6 AM local time
        today_sunrise = datetime.combine(
            for_date,
            datetime.min.time().replace(hour=6),
            tzinfo=tz
        ).astimezone(utc)

        tomorrow_sunrise = datetime.combine(
            for_date + timedelta(days=1),
            datetime.min.time().replace(hour=6),
            tzinfo=tz
        ).astimezone(utc)

    return today_sunrise, tomorrow_sunrise


def get_sunrise_info_for_user(
    user_timezone: Optional[str] = None,
    user_latitude: Optional[float] = None,
    user_longitude: Optional[float] = None,
    reference_time: Optional[datetime] = None
) -> dict:
    """
    Get complete sunrise information for a user.

    Determines which "day" (sunrise-to-sunrise) the user is currently in,
    and returns all relevant timestamps.

    Args:
        user_timezone: User's IANA timezone (or None for default)
        user_latitude: User's latitude (or None)
        user_longitude: User's longitude (or None)
        reference_time: Time to calculate for (default: now)

    Returns:
        {
            "day_key": "2026-01-25",           # Date identifier for this day
            "day_sunrise_utc": datetime,        # When this day started
            "next_sunrise_utc": datetime,       # When this day ends
            "timezone": str                     # Timezone used
        }
    """
    # Determine timezone
    timezone = user_timezone or DEFAULT_TIMEZONE

    # Determine coordinates
    if user_latitude is not None and user_longitude is not None:
        latitude = user_latitude
        longitude = user_longitude
    else:
        # Use representative coordinates for the timezone
        latitude, longitude = get_coordinates_for_timezone(timezone)

    # Get reference time in UTC
    utc = ZoneInfo("UTC")
    if reference_time is None:
        now_utc = datetime.now(utc)
    elif reference_time.tzinfo is None:
        now_utc = reference_time.replace(tzinfo=utc)
    else:
        now_utc = reference_time.astimezone(utc)

    # Convert to user's local time to get the calendar date
    tz = ZoneInfo(timezone)
    local_now = now_utc.astimezone(tz)
    local_date = local_now.date()

    # Get sunrise times for today and yesterday
    today_sunrise, tomorrow_sunrise = get_sunrise_times(
        latitude, longitude, timezone, local_date
    )
    yesterday_sunrise, today_sunrise_alt = get_sunrise_times(
        latitude, longitude, timezone, local_date - timedelta(days=1)
    )

    # Determine which "day" we're in (sunrise-to-sunrise)
    if now_utc >= today_sunrise:
        # After today's sunrise - we're in "today's" day
        day_sunrise = today_sunrise
        next_sunrise = tomorrow_sunrise
        day_key = local_date.isoformat()
    else:
        # Before today's sunrise - still in "yesterday's" day
        day_sunrise = yesterday_sunrise
        next_sunrise = today_sunrise
        day_key = (local_date - timedelta(days=1)).isoformat()

    return {
        "day_key": day_key,
        "day_sunrise_utc": day_sunrise,
        "next_sunrise_utc": next_sunrise,
        "timezone": timezone
    }


def get_day_key_for_user(
    user_timezone: Optional[str] = None,
    user_latitude: Optional[float] = None,
    user_longitude: Optional[float] = None,
    reference_time: Optional[datetime] = None
) -> str:
    """
    Get just the day_key for a user's current sunrise-based day.

    Convenience function when you only need the day_key.

    Args:
        user_timezone: User's IANA timezone (or None for default)
        user_latitude: User's latitude (or None)
        user_longitude: User's longitude (or None)
        reference_time: Time to calculate for (default: now)

    Returns:
        Day key string in YYYY-MM-DD format
    """
    info = get_sunrise_info_for_user(
        user_timezone, user_latitude, user_longitude, reference_time
    )
    return info["day_key"]
