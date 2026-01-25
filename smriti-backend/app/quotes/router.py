"""
API routes for the Today's Quote feature.

Endpoints:
- GET /api/quotes/today - Get today's quote status
- GET /api/quotes/history - Get quote history
- POST /api/internal/daily-quote-init - Cron: Initialize daily records
- POST /api/internal/daily-quote-push - Cron: Send pending pushes
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.quotes.dependencies import verify_cron_secret
from app.quotes.schemas import (
    TodayQuoteResponse,
    QuoteHistoryResponse,
    CronInitResponse,
    CronPushResponse
)
from app.quotes import service
from app.quotes.constants import DEFAULT_HISTORY_LIMIT, MAX_HISTORY_LIMIT

router = APIRouter(prefix="/quotes", tags=["quotes"])
internal_router = APIRouter(prefix="/internal", tags=["internal"])


# =============================================================================
# USER-FACING ENDPOINTS
# =============================================================================

@router.get(
    "/today",
    response_model=TodayQuoteResponse,
    summary="Get today's quote",
    description="""
    Get the current status of today's quote for the authenticated user.

    Returns one of three states:
    - **delivered**: Quote is available (has_quote=true, quote object present)
    - **pending**: Quote will arrive later today (has_quote=false)
    - **unavailable**: No quote available today (has_quote=false)

    The "day" is defined as sunrise-to-sunrise at the user's location.
    """
)
async def get_today_quote(
    current_user: UserResponse = Depends(get_current_user)
) -> TodayQuoteResponse:
    """Get today's quote status for the current user."""
    # Extract location from user
    user_lat = None
    user_lng = None
    if current_user.location:
        user_lat = current_user.location.latitude
        user_lng = current_user.location.longitude

    return await service.get_today_quote(
        user_id=str(current_user.id),
        user_timezone=current_user.timezone,
        user_latitude=user_lat,
        user_longitude=user_lng
    )


@router.get(
    "/history",
    response_model=QuoteHistoryResponse,
    summary="Get quote history",
    description="""
    Get the authenticated user's quote history.

    Returns a paginated list of past quotes, newest first.
    Only includes days where a quote was actually delivered.
    """
)
async def get_quote_history(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of quotes to skip (for pagination)"
    ),
    limit: int = Query(
        default=DEFAULT_HISTORY_LIMIT,
        ge=1,
        le=MAX_HISTORY_LIMIT,
        description="Maximum number of quotes to return"
    ),
    current_user: UserResponse = Depends(get_current_user)
) -> QuoteHistoryResponse:
    """Get quote history for the current user."""
    return await service.get_quote_history(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )


# =============================================================================
# INTERNAL CRON ENDPOINTS
# =============================================================================

@internal_router.post(
    "/daily-quote-init",
    response_model=CronInitResponse,
    summary="Initialize daily quote records",
    description="""
    **Cron Job 1: Daily Quote Initialization**

    Run this hourly. For each user:
    1. Determine their current day (based on sunrise at their location)
    2. If no record exists for this day, create one
    3. Schedule a random push time within the day

    Requires X-Cron-Secret header.
    """,
    responses={
        200: {"description": "Initialization complete"},
        401: {"description": "Invalid cron secret"},
        500: {"description": "Server error or CRON_SECRET not configured"}
    }
)
async def daily_quote_init(
    _: None = Depends(verify_cron_secret)
) -> CronInitResponse:
    """Initialize daily quote records for all users."""
    return await service.initialize_daily_quotes()


@internal_router.post(
    "/daily-quote-push",
    response_model=CronPushResponse,
    summary="Send pending push notifications",
    description="""
    **Cron Job 2: Push Notification Sender**

    Run this every 5-10 minutes. For each pending record where scheduled time has passed:
    1. Pick a random quote from posts
    2. Send push notification to user's devices
    3. Mark record as sent

    Requires X-Cron-Secret header.
    """,
    responses={
        200: {"description": "Push processing complete"},
        401: {"description": "Invalid cron secret"},
        500: {"description": "Server error or CRON_SECRET not configured"}
    }
)
async def daily_quote_push(
    _: None = Depends(verify_cron_secret)
) -> CronPushResponse:
    """Send pending push notifications."""
    return await service.send_pending_pushes()
