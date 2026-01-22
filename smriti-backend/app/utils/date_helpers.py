"""
Date and time utility functions.
"""
from datetime import datetime, timezone
from typing import Optional


def get_current_timestamp() -> datetime:
    """
    Get current UTC timestamp.
    
    Returns:
        Current datetime in UTC
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object
        format_string: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_string)


def parse_datetime(date_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse datetime string.
    
    Args:
        date_string: Date string to parse
        format_string: Format string
        
    Returns:
        Parsed datetime or None if invalid
    """
    try:
        return datetime.strptime(date_string, format_string)
    except (ValueError, TypeError):
        return None


def is_recent(dt: datetime, minutes: int = 5) -> bool:
    """
    Check if datetime is within recent time window.
    
    Args:
        dt: Datetime to check
        minutes: Time window in minutes
        
    Returns:
        True if datetime is within window
    """
    now = get_current_timestamp()
    diff = (now - dt.replace(tzinfo=timezone.utc)).total_seconds() / 60
    return 0 <= diff <= minutes
