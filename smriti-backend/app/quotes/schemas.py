"""
Pydantic schemas for the Today's Quote feature.

These models define the request/response structures for quote-related endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class QuoteStatus(str, Enum):
    """Status of today's quote for a user"""
    DELIVERED = "delivered"    # Quote has been sent and is available
    PENDING = "pending"        # Quote will arrive later today
    UNAVAILABLE = "unavailable"  # No quote available (no usable posts)


# =============================================================================
# NESTED MODELS
# =============================================================================

class QuoteAuthor(BaseModel):
    """Author information for a quote"""
    user_id: Optional[str] = Field(
        None,
        description="User ID of the post author"
    )
    username: Optional[str] = Field(
        None,
        description="Username of the post author"
    )


class QuoteData(BaseModel):
    """Complete quote data returned to the client"""
    text: str = Field(
        ...,
        description="The quote text (max 200 characters)"
    )
    author: QuoteAuthor = Field(
        ...,
        description="Author of the original post"
    )
    post_id: Optional[str] = Field(
        None,
        description="ID of the source post (for 'View Full Post' feature)"
    )
    day_key: str = Field(
        ...,
        description="The sunrise-based day identifier (YYYY-MM-DD)"
    )
    received_at: datetime = Field(
        ...,
        description="When the quote was sent/received (UTC)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The best time to plant a tree was 20 years ago. The second best time is now.",
                "author": {
                    "user_id": "507f1f77bcf86cd799439012",
                    "username": "wisdom_seeker"
                },
                "post_id": "507f1f77bcf86cd799439013",
                "day_key": "2026-01-25",
                "received_at": "2026-01-25T14:32:00Z"
            }
        }


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class TodayQuoteResponse(BaseModel):
    """
    Response for GET /api/quotes/today

    Three possible states:
    1. has_quote=True, status=delivered: Quote is available
    2. has_quote=False, status=pending: Quote will arrive later
    3. has_quote=False, status=unavailable: No quote today
    """
    has_quote: bool = Field(
        ...,
        description="Whether a quote is available"
    )
    status: QuoteStatus = Field(
        ...,
        description="Current status of today's quote"
    )
    quote: Optional[QuoteData] = Field(
        None,
        description="The quote data (only present when has_quote=True)"
    )
    message: Optional[str] = Field(
        None,
        description="Human-readable status message (when has_quote=False)"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "Quote delivered",
                    "value": {
                        "has_quote": True,
                        "status": "delivered",
                        "quote": {
                            "text": "The only way to do great work is to love what you do.",
                            "author": {"user_id": "123", "username": "steve"},
                            "post_id": "456",
                            "day_key": "2026-01-25",
                            "received_at": "2026-01-25T14:32:00Z"
                        },
                        "message": None
                    }
                },
                {
                    "summary": "Quote pending",
                    "value": {
                        "has_quote": False,
                        "status": "pending",
                        "quote": None,
                        "message": "Your quote will arrive later today"
                    }
                },
                {
                    "summary": "Quote unavailable",
                    "value": {
                        "has_quote": False,
                        "status": "unavailable",
                        "quote": None,
                        "message": "No quote available today"
                    }
                }
            ]
        }


class QuoteHistoryItem(BaseModel):
    """Single item in quote history"""
    text: str = Field(
        ...,
        description="The quote text"
    )
    author: QuoteAuthor = Field(
        ...,
        description="Author of the original post"
    )
    post_id: Optional[str] = Field(
        None,
        description="ID of the source post"
    )
    day_key: str = Field(
        ...,
        description="The day this quote was for (YYYY-MM-DD)"
    )
    received_at: datetime = Field(
        ...,
        description="When the quote was received (UTC)"
    )


class QuoteHistoryResponse(BaseModel):
    """
    Response for GET /api/quotes/history

    Paginated list of past quotes, newest first.
    Only includes days where a quote was actually delivered.
    """
    quotes: List[QuoteHistoryItem] = Field(
        ...,
        description="List of past quotes"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of quotes in history"
    )
    skip: int = Field(
        ...,
        ge=0,
        description="Number of quotes skipped (for pagination)"
    )
    limit: int = Field(
        ...,
        ge=1,
        description="Maximum quotes returned"
    )
    has_more: bool = Field(
        ...,
        description="Whether more quotes exist beyond this page"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "quotes": [
                    {
                        "text": "Be yourself; everyone else is already taken.",
                        "author": {"user_id": "123", "username": "oscar_fan"},
                        "post_id": "789",
                        "day_key": "2026-01-24",
                        "received_at": "2026-01-24T09:15:00Z"
                    }
                ],
                "total": 45,
                "skip": 0,
                "limit": 20,
                "has_more": True
            }
        }


# =============================================================================
# INTERNAL MODELS (used by cron jobs)
# =============================================================================

class CronInitResponse(BaseModel):
    """Response from daily quote initialization cron job"""
    initialized_count: int = Field(
        ...,
        ge=0,
        description="Number of new daily quote records created"
    )
    skipped_count: int = Field(
        ...,
        ge=0,
        description="Number of users already initialized for today"
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Number of users that failed to initialize"
    )


class CronPushResponse(BaseModel):
    """Response from daily quote push sender cron job"""
    processed_count: int = Field(
        ...,
        ge=0,
        description="Total records whose scheduled time passed"
    )
    sent_count: int = Field(
        ...,
        ge=0,
        description="Number of push notifications successfully sent"
    )
    no_quote_count: int = Field(
        default=0,
        ge=0,
        description="Number skipped due to no usable posts"
    )
    no_tokens_count: int = Field(
        default=0,
        ge=0,
        description="Number where quote saved but no devices to push to"
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Number of failures"
    )


# =============================================================================
# DATABASE DOCUMENT MODEL
# =============================================================================

class DailyQuoteDocument(BaseModel):
    """
    Represents a document in the user_daily_quotes collection.

    This is used internally for type safety when working with DB documents.
    """
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    day_key: str

    # Scheduling
    day_sunrise_utc: datetime
    next_sunrise_utc: datetime
    scheduled_push_time_utc: datetime

    # Delivery status
    push_sent: bool = False
    push_sent_at_utc: Optional[datetime] = None

    # Quote data (set when push is sent)
    quote_text: Optional[str] = None
    source_post_id: Optional[str] = None
    source_author_user_id: Optional[str] = None
    source_author_username: Optional[str] = None

    # Timestamps
    created_at_utc: datetime
    updated_at_utc: datetime

    class Config:
        populate_by_name = True


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_today_quote_response(
    has_quote: bool,
    status: QuoteStatus,
    quote_data: Optional[dict] = None,
    message: Optional[str] = None
) -> TodayQuoteResponse:
    """
    Build a TodayQuoteResponse from components.

    Args:
        has_quote: Whether a quote is available
        status: Current status
        quote_data: Dict with quote fields (if has_quote=True)
        message: Status message (if has_quote=False)

    Returns:
        TodayQuoteResponse instance
    """
    quote = None
    if has_quote and quote_data:
        quote = QuoteData(
            text=quote_data["text"],
            author=QuoteAuthor(
                user_id=quote_data.get("author_user_id"),
                username=quote_data.get("author_username")
            ),
            post_id=quote_data.get("post_id"),
            day_key=quote_data["day_key"],
            received_at=quote_data["received_at"]
        )

    return TodayQuoteResponse(
        has_quote=has_quote,
        status=status,
        quote=quote,
        message=message
    )


def build_quote_history_item(doc: dict) -> QuoteHistoryItem:
    """
    Build a QuoteHistoryItem from a database document.

    Args:
        doc: Database document from user_daily_quotes collection

    Returns:
        QuoteHistoryItem instance
    """
    return QuoteHistoryItem(
        text=doc["quote_text"],
        author=QuoteAuthor(
            user_id=doc.get("source_author_user_id"),
            username=doc.get("source_author_username")
        ),
        post_id=doc.get("source_post_id"),
        day_key=doc["day_key"],
        received_at=doc.get("push_sent_at_utc") or doc["created_at_utc"]
    )
