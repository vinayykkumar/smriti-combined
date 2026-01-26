"""
Constants for Circles module.
"""
import secrets
import string

# Collection name
COLLECTION_NAME = "circles"

# Limits
MAX_MEMBERS_PER_CIRCLE = 5
MAX_CIRCLES_PER_USER = 20
INVITE_CODE_LENGTH = 8

# Circle name constraints
MIN_CIRCLE_NAME_LENGTH = 2
MAX_CIRCLE_NAME_LENGTH = 40
MAX_CIRCLE_DESCRIPTION_LENGTH = 200

# Color palette for circles (warm, calm colors matching Smriti theme)
CIRCLE_COLORS = [
    "#8D6E63",  # Warm Brown (default)
    "#7986CB",  # Soft Indigo
    "#81C784",  # Sage Green
    "#F48FB1",  # Dusty Rose
    "#FFB74D",  # Soft Amber
    "#4DB6AC",  # Teal
    "#9575CD",  # Lavender
    "#A1887F",  # Taupe
    "#90A4AE",  # Slate
    "#DCE775",  # Soft Lime
    "#E57373",  # Soft Red
    "#64B5F6",  # Sky Blue
    "#BA68C8",  # Orchid
    "#4DD0E1",  # Cyan
]

# Default emojis for circle selection
CIRCLE_EMOJIS = [
    "🪷", "🌸", "🎓", "📚", "🧘", "🌙", "☕", "🎵",
    "✨", "🌿", "🔮", "💫", "🦋", "🌊", "🍃", "🕊️",
    "🏠", "💝", "🌻", "🎯", "🌈", "🔥", "⭐", "🌺",
]

# Characters for invite code (excluding confusing chars: 0/O, 1/I/L)
INVITE_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def generate_invite_code() -> str:
    """
    Generate a unique 8-character invite code.
    Uses uppercase letters and digits, excluding confusing characters.

    Returns:
        8-character alphanumeric string (e.g., "A7X2K9M4")
    """
    return ''.join(secrets.choice(INVITE_CODE_ALPHABET) for _ in range(INVITE_CODE_LENGTH))


def get_random_color() -> str:
    """
    Get a random color from the circle color palette.

    Returns:
        Hex color string (e.g., "#8D6E63")
    """
    return secrets.choice(CIRCLE_COLORS)


def is_valid_color(color: str) -> bool:
    """
    Check if color is a valid hex color from our palette.

    Args:
        color: Hex color string

    Returns:
        True if valid, False otherwise
    """
    if not color:
        return False
    return color.upper() in [c.upper() for c in CIRCLE_COLORS]
