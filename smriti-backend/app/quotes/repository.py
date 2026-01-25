"""
Database operations for the Today's Quote feature.

This module handles all interactions with the user_daily_quotes collection.
"""

from datetime import datetime
from typing import Optional, List, Tuple
from zoneinfo import ZoneInfo
from bson import ObjectId
from pymongo import ReturnDocument

from app.database.connection import get_database
from app.quotes.constants import (
    COLLECTION_NAME,
    DEFAULT_HISTORY_LIMIT,
    MAX_HISTORY_LIMIT
)


# =============================================================================
# SINGLE DOCUMENT OPERATIONS
# =============================================================================

async def get_quote_for_user_day(user_id: str, day_key: str) -> Optional[dict]:
    """
    Get the daily quote record for a specific user and day.

    Args:
        user_id: User's ObjectId as string
        day_key: Day identifier in YYYY-MM-DD format

    Returns:
        Document dict if found, None otherwise
    """
    db = get_database()
    return await db[COLLECTION_NAME].find_one({
        "user_id": user_id,
        "day_key": day_key
    })


async def check_quote_exists(user_id: str, day_key: str) -> bool:
    """
    Check if a daily quote record exists for a user and day.

    More efficient than get_quote_for_user_day when you only need existence check.

    Args:
        user_id: User's ObjectId as string
        day_key: Day identifier in YYYY-MM-DD format

    Returns:
        True if record exists, False otherwise
    """
    db = get_database()
    count = await db[COLLECTION_NAME].count_documents(
        {"user_id": user_id, "day_key": day_key},
        limit=1
    )
    return count > 0


# =============================================================================
# CREATE OPERATIONS
# =============================================================================

async def create_daily_quote_record(
    user_id: str,
    day_key: str,
    day_sunrise_utc: datetime,
    next_sunrise_utc: datetime,
    scheduled_push_time_utc: datetime
) -> str:
    """
    Create a new daily quote record for a user.

    This is called by the day initializer cron job when a user enters a new day.

    Args:
        user_id: User's ObjectId as string
        day_key: Day identifier in YYYY-MM-DD format
        day_sunrise_utc: Start of this day (sunrise) in UTC
        next_sunrise_utc: End of this day (next sunrise) in UTC
        scheduled_push_time_utc: Random time to send the push notification

    Returns:
        Inserted document's _id as string

    Raises:
        DuplicateKeyError: If record already exists (unique constraint)
    """
    db = get_database()
    now_utc = datetime.now(ZoneInfo("UTC"))

    document = {
        "user_id": user_id,
        "day_key": day_key,
        "day_sunrise_utc": day_sunrise_utc,
        "next_sunrise_utc": next_sunrise_utc,
        "scheduled_push_time_utc": scheduled_push_time_utc,
        "push_sent": False,
        "push_sent_at_utc": None,
        "quote_text": None,
        "source_post_id": None,
        "source_author_user_id": None,
        "source_author_username": None,
        "created_at_utc": now_utc,
        "updated_at_utc": now_utc
    }

    result = await db[COLLECTION_NAME].insert_one(document)
    return str(result.inserted_id)


# =============================================================================
# UPDATE OPERATIONS
# =============================================================================

async def mark_quote_sent(
    record_id: str,
    quote_text: Optional[str],
    source_post_id: Optional[str] = None,
    source_author_user_id: Optional[str] = None,
    source_author_username: Optional[str] = None
) -> bool:
    """
    Mark a daily quote record as sent and store the quote data.

    Called by the push sender cron job after sending (or attempting to send) a quote.

    Args:
        record_id: Document's _id as string
        quote_text: The extracted quote (None if no usable posts)
        source_post_id: ID of the source post
        source_author_user_id: User ID of the post author
        source_author_username: Username of the post author

    Returns:
        True if document was updated, False if not found
    """
    db = get_database()
    now_utc = datetime.now(ZoneInfo("UTC"))

    result = await db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(record_id)},
        {
            "$set": {
                "push_sent": True,
                "push_sent_at_utc": now_utc,
                "quote_text": quote_text,
                "source_post_id": source_post_id,
                "source_author_user_id": source_author_user_id,
                "source_author_username": source_author_username,
                "updated_at_utc": now_utc
            }
        }
    )

    return result.modified_count > 0


async def mark_quote_sent_by_user_day(
    user_id: str,
    day_key: str,
    quote_text: Optional[str],
    source_post_id: Optional[str] = None,
    source_author_user_id: Optional[str] = None,
    source_author_username: Optional[str] = None
) -> bool:
    """
    Mark a daily quote as sent using user_id and day_key.

    Alternative to mark_quote_sent when you don't have the record _id.

    Args:
        user_id: User's ObjectId as string
        day_key: Day identifier in YYYY-MM-DD format
        quote_text: The extracted quote (None if no usable posts)
        source_post_id: ID of the source post
        source_author_user_id: User ID of the post author
        source_author_username: Username of the post author

    Returns:
        True if document was updated, False if not found
    """
    db = get_database()
    now_utc = datetime.now(ZoneInfo("UTC"))

    result = await db[COLLECTION_NAME].update_one(
        {"user_id": user_id, "day_key": day_key},
        {
            "$set": {
                "push_sent": True,
                "push_sent_at_utc": now_utc,
                "quote_text": quote_text,
                "source_post_id": source_post_id,
                "source_author_user_id": source_author_user_id,
                "source_author_username": source_author_username,
                "updated_at_utc": now_utc
            }
        }
    )

    return result.modified_count > 0


# =============================================================================
# QUERY OPERATIONS
# =============================================================================

async def get_pending_pushes(before_time: datetime) -> List[dict]:
    """
    Get all daily quote records that are due for sending.

    Query: scheduled_push_time_utc <= before_time AND push_sent = false

    Args:
        before_time: Only include records scheduled before this time

    Returns:
        List of document dicts
    """
    db = get_database()

    cursor = db[COLLECTION_NAME].find({
        "push_sent": False,
        "scheduled_push_time_utc": {"$lte": before_time}
    })

    # Limit to prevent memory issues with large backlogs
    return await cursor.to_list(length=1000)


async def get_quote_history(
    user_id: str,
    skip: int = 0,
    limit: int = DEFAULT_HISTORY_LIMIT
) -> Tuple[List[dict], int]:
    """
    Get a user's quote history (past quotes only).

    Only returns records where:
    - push_sent = true
    - quote_text is not null (skips days with no available quote)

    Results are sorted by day_key descending (newest first).

    Args:
        user_id: User's ObjectId as string
        skip: Number of records to skip (for pagination)
        limit: Maximum records to return

    Returns:
        Tuple of (list of documents, total count)
    """
    db = get_database()

    # Clamp limit to max
    limit = min(limit, MAX_HISTORY_LIMIT)

    query = {
        "user_id": user_id,
        "push_sent": True,
        "quote_text": {"$ne": None}
    }

    # Get total count
    total = await db[COLLECTION_NAME].count_documents(query)

    # Get paginated results
    cursor = db[COLLECTION_NAME].find(query)\
        .sort("day_key", -1)\
        .skip(skip)\
        .limit(limit)

    documents = await cursor.to_list(length=limit)

    return documents, total


async def get_users_without_today_record(day_keys_by_user: dict) -> List[str]:
    """
    Find users who don't have a record for their current day.

    This is used by the day initializer to find users needing initialization.

    Args:
        day_keys_by_user: Dict mapping user_id -> day_key

    Returns:
        List of user_ids that need records created

    Note: This is an optimization - in practice, the initializer iterates
    all users and checks individually, which is simpler and handles
    edge cases better.
    """
    # For now, return empty - the initializer does individual checks
    # This method is here for potential future optimization
    return []


# =============================================================================
# AGGREGATION OPERATIONS
# =============================================================================

async def get_quote_stats(user_id: str) -> dict:
    """
    Get statistics about a user's quote history.

    Args:
        user_id: User's ObjectId as string

    Returns:
        Dict with stats: total_quotes, first_quote_date, last_quote_date
    """
    db = get_database()

    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "push_sent": True,
                "quote_text": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_quotes": {"$sum": 1},
                "first_quote_date": {"$min": "$day_key"},
                "last_quote_date": {"$max": "$day_key"}
            }
        }
    ]

    cursor = db[COLLECTION_NAME].aggregate(pipeline)
    results = await cursor.to_list(length=1)

    if not results:
        return {
            "total_quotes": 0,
            "first_quote_date": None,
            "last_quote_date": None
        }

    return {
        "total_quotes": results[0]["total_quotes"],
        "first_quote_date": results[0]["first_quote_date"],
        "last_quote_date": results[0]["last_quote_date"]
    }


# =============================================================================
# INDEX SETUP
# =============================================================================

async def setup_indexes() -> None:
    """
    Create indexes for the user_daily_quotes collection.

    Should be called during application startup or via a setup script.

    Indexes:
    1. (user_id, day_key) - unique: Primary lookup, ensures one quote per user per day
    2. (push_sent, scheduled_push_time_utc): For cron job to find pending pushes
    3. (user_id, push_sent, day_key): For history queries
    """
    db = get_database()
    collection = db[COLLECTION_NAME]

    # Index 1: Unique constraint - one record per user per day
    await collection.create_index(
        [("user_id", 1), ("day_key", -1)],
        unique=True,
        name="user_day_unique"
    )

    # Index 2: For cron job query (find pending pushes)
    await collection.create_index(
        [("push_sent", 1), ("scheduled_push_time_utc", 1)],
        name="pending_push_lookup"
    )

    # Index 3: For history query (user's past quotes, sorted by day)
    await collection.create_index(
        [("user_id", 1), ("push_sent", 1), ("day_key", -1)],
        name="user_history_lookup"
    )


# =============================================================================
# CLEANUP OPERATIONS (for maintenance)
# =============================================================================

async def delete_old_quotes(before_date: str) -> int:
    """
    Delete quote records older than a certain date.

    This is for maintenance/cleanup if needed in the future.
    Currently quotes are kept forever as per requirements.

    Args:
        before_date: Delete records with day_key before this date (YYYY-MM-DD)

    Returns:
        Number of documents deleted
    """
    db = get_database()

    result = await db[COLLECTION_NAME].delete_many({
        "day_key": {"$lt": before_date}
    })

    return result.deleted_count
