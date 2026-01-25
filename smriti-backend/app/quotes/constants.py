"""
Constants for the Today's Quote feature.

These values define the behavior of quote generation, scheduling, and delivery.
"""

# =============================================================================
# TIMEZONE & LOCATION DEFAULTS
# =============================================================================

# Default timezone when user hasn't set one
# UTC is the most neutral choice - no daylight saving complications
DEFAULT_TIMEZONE = "UTC"

# Default location (latitude, longitude) when user hasn't set one
# (0, 0) is on the equator at the Prime Meridian
# At the equator, sunrise is approximately 6:00 AM year-round, which is predictable
DEFAULT_LATITUDE = 0.0
DEFAULT_LONGITUDE = 0.0


# =============================================================================
# QUOTE EXTRACTION
# =============================================================================

# Maximum length of extracted quote in characters
# 200 chars is readable, impactful, and fits well on mobile screens
MAX_QUOTE_LENGTH = 200

# Minimum length for a quote to be considered valid
# Prevents very short, meaningless quotes
MIN_QUOTE_LENGTH = 10

# Number of random post candidates to fetch when picking a quote
# Higher number = more likely to find a usable quote, but more DB load
QUOTE_CANDIDATES_COUNT = 10


# =============================================================================
# SCHEDULING
# =============================================================================

# When a user's scheduled time is in the past (they just entered a new day),
# reschedule to somewhere between these minutes from now
RESCHEDULE_MIN_MINUTES = 5
RESCHEDULE_MAX_MINUTES = 60

# Maximum devices per user to send push notifications to
MAX_DEVICES_PER_USER = 50


# =============================================================================
# HISTORY
# =============================================================================

# Default pagination limit for quote history
DEFAULT_HISTORY_LIMIT = 20

# Maximum pagination limit for quote history
MAX_HISTORY_LIMIT = 50


# =============================================================================
# PUSH NOTIFICATION
# =============================================================================

# Push notification title
PUSH_NOTIFICATION_TITLE = "Today's Quote"

# Maximum length of quote preview in push notification body
PUSH_PREVIEW_MAX_LENGTH = 100

# Data type identifier for the frontend to recognize quote notifications
PUSH_DATA_TYPE = "today_quote"


# =============================================================================
# COLLECTION NAME
# =============================================================================

# MongoDB collection name for daily quotes
COLLECTION_NAME = "user_daily_quotes"
