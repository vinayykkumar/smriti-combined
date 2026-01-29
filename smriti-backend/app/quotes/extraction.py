"""
Quote extraction utilities for the Today's Quote feature.

Extracts readable, meaningful quotes from posts in the database.
"""

import re
import random
from typing import Optional, Dict, Any

from app.database.connection import get_database
from app.quotes.constants import (
    MAX_QUOTE_LENGTH,
    MIN_QUOTE_LENGTH,
    QUOTE_CANDIDATES_COUNT,
)


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.

    Handles common abbreviations and punctuation patterns.

    Args:
        text: Text to split

    Returns:
        List of sentence strings
    """
    if not text:
        return []

    # Protect common abbreviations
    protected = text
    abbreviations = [
        'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
        'vs.', 'etc.', 'i.e.', 'e.g.', 'St.', 'Mt.', 'Inc.',
        'Ltd.', 'Corp.', 'No.', 'Vol.', 'Rev.', 'Ed.'
    ]
    for abbr in abbreviations:
        protected = protected.replace(abbr, abbr.replace('.', '<DOT>'))

    # Split on sentence-ending punctuation followed by space or end
    pattern = r'(?<=[.!?])\s+'
    parts = re.split(pattern, protected)

    # Restore abbreviations and clean up
    sentences = []
    for part in parts:
        restored = part.replace('<DOT>', '.')
        cleaned = restored.strip()
        if cleaned:
            sentences.append(cleaned)

    return sentences


def truncate_at_word_boundary(text: str, max_length: int) -> Optional[str]:
    """
    Truncate text at a word boundary, adding ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length including ellipsis

    Returns:
        Truncated text with ellipsis, or None if can't truncate meaningfully
    """
    if len(text) <= max_length:
        return text

    # Leave room for "..."
    truncated = text[:max_length - 3]

    # Find last space
    last_space = truncated.rfind(' ')

    if last_space > MIN_QUOTE_LENGTH:
        return truncated[:last_space].rstrip('.,;:') + "..."

    return None


def extract_quote_from_text(text: str) -> Optional[str]:
    """
    Extract a readable quote (max 200 chars) from text.

    Strategy:
    1. If entire text fits, use it
    2. Try to fit complete sentences
    3. If needed, truncate at word boundary

    Args:
        text: Source text to extract from

    Returns:
        Extracted quote string, or None if text is unusable
    """
    if not text:
        return None

    # Clean up whitespace
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    if len(text) < MIN_QUOTE_LENGTH:
        return None

    # If entire text fits, use it
    if len(text) <= MAX_QUOTE_LENGTH:
        return text

    # Try to get complete sentences
    sentences = split_into_sentences(text)

    if not sentences:
        # No sentence structure, truncate at word boundary
        return truncate_at_word_boundary(text, MAX_QUOTE_LENGTH)

    # Build quote from sentences until we hit limit
    result = ""
    for sentence in sentences:
        candidate = f"{result} {sentence}".strip() if result else sentence

        if len(candidate) <= MAX_QUOTE_LENGTH:
            result = candidate
        elif not result:
            # First sentence is too long, truncate it
            return truncate_at_word_boundary(sentence, MAX_QUOTE_LENGTH)
        else:
            # Can't fit more sentences
            break

    if len(result) >= MIN_QUOTE_LENGTH:
        return result

    return None


async def pick_random_quote() -> Optional[Dict[str, Any]]:
    """
    Pick a random post and extract a quote from it.

    Samples multiple candidates from the database and tries each
    until finding one with usable text.

    Returns:
        {
            "quote_text": "The extracted quote...",
            "post_id": "507f1f77bcf86cd799439011",
            "author_user_id": "507f1f77bcf86cd799439012",
            "author_username": "john_doe"
        }
        Or None if no posts have usable text.
    """
    db = await get_database()

    # Aggregation pipeline to get random posts with text content
    pipeline = [
        # Match posts that have title OR text_content
        {
            "$match": {
                "$or": [
                    {"title": {"$exists": True, "$nin": ["", None]}},
                    {"text_content": {"$exists": True, "$nin": ["", None]}}
                ]
            }
        },
        # Random sample
        {"$sample": {"size": QUOTE_CANDIDATES_COUNT}},
        # Only fetch fields we need
        {
            "$project": {
                "title": 1,
                "text_content": 1,
                "author": 1
            }
        }
    ]

    cursor = db.posts.aggregate(pipeline)
    candidates = await cursor.to_list(length=QUOTE_CANDIDATES_COUNT)

    if not candidates:
        return None

    # Shuffle for extra randomness
    random.shuffle(candidates)

    # Try each candidate until we get a usable quote
    for post in candidates:
        # Combine title and text_content
        parts = []
        title = post.get("title", "")
        text_content = post.get("text_content", "")

        if title and title.strip():
            parts.append(title.strip())
        if text_content and text_content.strip():
            parts.append(text_content.strip())

        if not parts:
            continue

        combined = " ".join(parts)
        quote_text = extract_quote_from_text(combined)

        if quote_text:
            author = post.get("author", {})
            return {
                "quote_text": quote_text,
                "post_id": str(post["_id"]),
                "author_user_id": author.get("user_id"),
                "author_username": author.get("username")
            }

    # No candidates had usable text
    return None


async def get_posts_with_text_count() -> int:
    """
    Get count of posts that have usable text content.

    Useful for checking if quote extraction is possible.

    Returns:
        Number of posts with title or text_content
    """
    db = await get_database()

    count = await db.posts.count_documents({
        "$or": [
            {"title": {"$exists": True, "$nin": ["", None]}},
            {"text_content": {"$exists": True, "$nin": ["", None]}}
        ]
    })

    return count
