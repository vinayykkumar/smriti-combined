"""
Business logic for the Today's Quote feature.

This module contains the core service functions for:
- Getting today's quote for a user
- Getting quote history
- Cron jobs for initialization and push notifications
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from zoneinfo import ZoneInfo

from app.database.connection import get_database
from app.quotes import repository
from app.quotes.extraction import pick_random_quote
from app.quotes.sunrise import get_sunrise_info_for_user, get_day_key_for_user
from app.quotes.schemas import (
    QuoteStatus,
    TodayQuoteResponse,
    QuoteHistoryResponse,
    CronInitResponse,
    CronPushResponse,
    build_today_quote_response,
    build_quote_history_item
)
from app.quotes.constants import DEFAULT_HISTORY_LIMIT
from app.notifications.repository import NotificationRepository
from app.utils.firebase import send_push_notification

logger = logging.getLogger(__name__)


# =============================================================================
# USER-FACING SERVICES
# =============================================================================

async def get_today_quote(
    user_id: str,
    user_timezone: Optional[str] = None,
    user_latitude: Optional[float] = None,
    user_longitude: Optional[float] = None
) -> TodayQuoteResponse:
    """
    Get today's quote status and data for a user.

    Determines the current "day" based on sunrise at user's location,
    then returns the quote if already delivered, or status if pending.

    Args:
        user_id: User's ObjectId as string
        user_timezone: User's IANA timezone (or None for default)
        user_latitude: User's latitude (or None)
        user_longitude: User's longitude (or None)

    Returns:
        TodayQuoteResponse with one of three states:
        - delivered: Quote is available
        - pending: Quote will arrive later today
        - unavailable: No quote available (no usable posts)
    """
    # Get current day info for user's location
    sunrise_info = get_sunrise_info_for_user(
        user_timezone, user_latitude, user_longitude
    )
    day_key = sunrise_info["day_key"]

    # Check if record exists for today
    record = await repository.get_quote_for_user_day(user_id, day_key)

    if not record:
        # No record for today - this shouldn't happen normally
        # (cron job should have created it), but handle gracefully
        return build_today_quote_response(
            has_quote=False,
            status=QuoteStatus.PENDING,
            message="Your quote will arrive soon"
        )

    if not record.get("push_sent"):
        # Quote scheduled but not yet sent
        return build_today_quote_response(
            has_quote=False,
            status=QuoteStatus.PENDING,
            message="Your quote will arrive later today"
        )

    # Push has been sent
    quote_text = record.get("quote_text")

    if not quote_text:
        # Push was marked sent but no quote (no usable posts)
        return build_today_quote_response(
            has_quote=False,
            status=QuoteStatus.UNAVAILABLE,
            message="No quote available today"
        )

    # Quote is available
    return build_today_quote_response(
        has_quote=True,
        status=QuoteStatus.DELIVERED,
        quote_data={
            "text": quote_text,
            "author_user_id": record.get("source_author_user_id"),
            "author_username": record.get("source_author_username"),
            "post_id": record.get("source_post_id"),
            "day_key": day_key,
            "received_at": record.get("push_sent_at_utc") or record["created_at_utc"]
        }
    )


async def get_quote_history(
    user_id: str,
    skip: int = 0,
    limit: int = DEFAULT_HISTORY_LIMIT
) -> QuoteHistoryResponse:
    """
    Get a user's quote history.

    Returns paginated list of past quotes, newest first.
    Only includes days where a quote was actually delivered.

    Args:
        user_id: User's ObjectId as string
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        QuoteHistoryResponse with quotes and pagination info
    """
    documents, total = await repository.get_quote_history(user_id, skip, limit)

    quotes = [build_quote_history_item(doc) for doc in documents]

    return QuoteHistoryResponse(
        quotes=quotes,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(quotes)) < total
    )


# =============================================================================
# CRON JOB SERVICES
# =============================================================================

async def initialize_daily_quotes() -> CronInitResponse:
    """
    Cron Job 1: Initialize daily quote records for all users.

    This should run hourly. For each user:
    1. Determine their current day (based on sunrise at their location)
    2. If they don't have a record for this day, create one
    3. Schedule a random push time within the day

    Returns:
        CronInitResponse with counts of initialized/skipped/errored users
    """
    db = get_database()
    utc = ZoneInfo("UTC")
    now_utc = datetime.now(utc)

    initialized_count = 0
    skipped_count = 0
    error_count = 0

    # Get all users
    cursor = db.users.find({}, {
        "_id": 1,
        "timezone": 1,
        "location": 1
    })
    users = await cursor.to_list(length=10000)

    logger.info(f"Daily quote init: Processing {len(users)} users")

    for user in users:
        try:
            user_id = str(user["_id"])
            user_timezone = user.get("timezone")

            # Get location if available
            location = user.get("location", {})
            user_lat = location.get("latitude") if location else None
            user_lng = location.get("longitude") if location else None

            # Get sunrise info for this user
            sunrise_info = get_sunrise_info_for_user(
                user_timezone, user_lat, user_lng, now_utc
            )

            day_key = sunrise_info["day_key"]
            day_sunrise = sunrise_info["day_sunrise_utc"]
            next_sunrise = sunrise_info["next_sunrise_utc"]

            # Check if record exists
            exists = await repository.check_quote_exists(user_id, day_key)

            if exists:
                skipped_count += 1
                continue

            # Generate random push time within the day
            scheduled_time = _generate_random_push_time(day_sunrise, next_sunrise, now_utc)

            # Create record
            await repository.create_daily_quote_record(
                user_id=user_id,
                day_key=day_key,
                day_sunrise_utc=day_sunrise,
                next_sunrise_utc=next_sunrise,
                scheduled_push_time_utc=scheduled_time
            )

            initialized_count += 1

        except Exception as e:
            logger.error(f"Error initializing daily quote for user {user.get('_id')}: {e}")
            error_count += 1

    logger.info(
        f"Daily quote init complete: initialized={initialized_count}, "
        f"skipped={skipped_count}, errors={error_count}"
    )

    return CronInitResponse(
        initialized_count=initialized_count,
        skipped_count=skipped_count,
        error_count=error_count
    )


async def send_pending_pushes() -> CronPushResponse:
    """
    Cron Job 2: Send pending push notifications.

    This should run every 5-10 minutes. For each pending record:
    1. Check if scheduled time has passed
    2. Pick a random quote from posts
    3. Send push notification to user's devices
    4. Mark record as sent

    Returns:
        CronPushResponse with counts of processed/sent/errored records
    """
    utc = ZoneInfo("UTC")
    now_utc = datetime.now(utc)
    db = get_database()
    notification_repo = NotificationRepository(db)

    processed_count = 0
    sent_count = 0
    no_quote_count = 0
    no_tokens_count = 0
    error_count = 0

    # Get all pending records whose time has come
    pending_records = await repository.get_pending_pushes(now_utc)

    logger.info(f"Push sender: Processing {len(pending_records)} pending records")

    for record in pending_records:
        processed_count += 1
        record_id = str(record["_id"])
        user_id = record["user_id"]

        try:
            # Pick a random quote
            quote_data = await pick_random_quote()

            if not quote_data:
                # No usable posts - mark as sent with no quote
                await repository.mark_quote_sent(record_id, None)
                no_quote_count += 1
                continue

            # Get user's device tokens
            tokens = await notification_repo.get_tokens_for_user(user_id)

            # Save quote data regardless of push
            await repository.mark_quote_sent(
                record_id=record_id,
                quote_text=quote_data["quote_text"],
                source_post_id=quote_data.get("post_id"),
                source_author_user_id=quote_data.get("author_user_id"),
                source_author_username=quote_data.get("author_username")
            )

            if not tokens:
                # Quote saved but no devices to push to
                no_tokens_count += 1
                continue

            # Send push notification
            push_sent = _send_quote_push(
                tokens=tokens,
                quote_text=quote_data["quote_text"],
                post_id=quote_data.get("post_id"),
                day_key=record["day_key"]
            )

            if push_sent:
                sent_count += 1
            else:
                # Push failed but quote is saved, user can still see it in app
                logger.warning(f"Push failed for user {user_id} but quote saved")

        except Exception as e:
            logger.error(f"Error processing record {record_id}: {e}")
            error_count += 1

    logger.info(
        f"Push sender complete: processed={processed_count}, sent={sent_count}, "
        f"no_quote={no_quote_count}, no_tokens={no_tokens_count}, errors={error_count}"
    )

    return CronPushResponse(
        processed_count=processed_count,
        sent_count=sent_count,
        no_quote_count=no_quote_count,
        no_tokens_count=no_tokens_count,
        error_count=error_count
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _generate_random_push_time(
    day_sunrise: datetime,
    next_sunrise: datetime,
    now_utc: datetime
) -> datetime:
    """
    Generate a random push time within the day.

    The push time is between:
    - Start: max(day_sunrise + 1 hour, now_utc + 5 minutes)
    - End: next_sunrise - 1 hour

    This ensures:
    - Push is at least 1 hour after sunrise (user is awake)
    - Push is at least 1 hour before next sunrise (reasonable hour)
    - Push is at least 5 minutes in the future (for processing)

    Args:
        day_sunrise: Start of this day (sunrise) in UTC
        next_sunrise: End of this day (next sunrise) in UTC
        now_utc: Current time in UTC

    Returns:
        Random datetime for scheduled push
    """
    # Earliest: sunrise + 1 hour, or now + 5 minutes (whichever is later)
    earliest = day_sunrise + timedelta(hours=1)
    min_delay = now_utc + timedelta(minutes=5)
    if min_delay > earliest:
        earliest = min_delay

    # Latest: next sunrise - 1 hour
    latest = next_sunrise - timedelta(hours=1)

    # Handle edge case where earliest >= latest
    if earliest >= latest:
        # Just schedule for now + 5-15 minutes
        return now_utc + timedelta(minutes=random.randint(5, 15))

    # Generate random time between earliest and latest
    window_seconds = int((latest - earliest).total_seconds())
    random_offset = random.randint(0, window_seconds)

    return earliest + timedelta(seconds=random_offset)


def _send_quote_push(
    tokens: List[str],
    quote_text: str,
    post_id: Optional[str],
    day_key: str
) -> bool:
    """
    Send push notification with today's quote.

    Args:
        tokens: List of FCM device tokens
        quote_text: The quote text to display
        post_id: Source post ID (for navigation)
        day_key: The day identifier

    Returns:
        True if at least one push succeeded, False otherwise
    """
    # Truncate quote for notification if needed
    title = "Today's Quote"
    body = quote_text[:100] + "..." if len(quote_text) > 100 else quote_text

    data = {
        "type": "today_quote",
        "day_key": day_key,
        "quote_text": quote_text
    }
    if post_id:
        data["post_id"] = post_id

    try:
        result = send_push_notification(
            tokens=tokens,
            title=title,
            body=body,
            data=data
        )
        return result.get("success", 0) > 0
    except Exception as e:
        logger.error(f"Push notification error: {e}")
        return False
