"""
Integration tests for Today's Quote API endpoints.

Tests:
- Schema validation for cron endpoints
- PATCH /api/users/me timezone validation
- Quote response structures
- Edge cases (missing author, long quotes, etc.)
"""

import pytest
from datetime import datetime


# =============================================================================
# TIMEZONE VALIDATION TESTS
# =============================================================================

class TestTimezoneValidation:
    """Test IANA timezone validation in UserUpdate schema"""

    def test_accepts_valid_us_timezone(self):
        """Should accept valid US timezone"""
        from app.users.schemas import UserUpdate

        update = UserUpdate(timezone="America/New_York")
        assert update.timezone == "America/New_York"

        update = UserUpdate(timezone="America/Los_Angeles")
        assert update.timezone == "America/Los_Angeles"

        update = UserUpdate(timezone="America/Chicago")
        assert update.timezone == "America/Chicago"

    def test_accepts_valid_asia_timezone(self):
        """Should accept valid Asian timezones"""
        from app.users.schemas import UserUpdate

        update = UserUpdate(timezone="Asia/Kolkata")
        assert update.timezone == "Asia/Kolkata"

        update = UserUpdate(timezone="Asia/Tokyo")
        assert update.timezone == "Asia/Tokyo"

        update = UserUpdate(timezone="Asia/Shanghai")
        assert update.timezone == "Asia/Shanghai"

    def test_accepts_valid_europe_timezone(self):
        """Should accept valid European timezones"""
        from app.users.schemas import UserUpdate

        update = UserUpdate(timezone="Europe/London")
        assert update.timezone == "Europe/London"

        update = UserUpdate(timezone="Europe/Paris")
        assert update.timezone == "Europe/Paris"

    def test_accepts_utc(self):
        """Should accept UTC"""
        from app.users.schemas import UserUpdate

        update = UserUpdate(timezone="UTC")
        assert update.timezone == "UTC"

    def test_rejects_invalid_timezone(self):
        """Should reject invalid timezone string"""
        from app.users.schemas import UserUpdate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(timezone="Invalid/Timezone")

        error = exc_info.value.errors()[0]
        assert "Invalid timezone" in str(error["msg"])

    def test_rejects_gibberish(self):
        """Should reject gibberish timezone strings"""
        from app.users.schemas import UserUpdate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UserUpdate(timezone="NotATimezone")

        with pytest.raises(ValidationError):
            UserUpdate(timezone="Foo/Bar/Baz")

    def test_timezone_is_optional(self):
        """Should allow omitting timezone"""
        from app.users.schemas import UserUpdate

        update = UserUpdate()
        assert update.timezone is None

    def test_location_without_timezone(self):
        """Should allow setting location without timezone"""
        from app.users.schemas import UserUpdate

        update = UserUpdate(latitude=40.7128, longitude=-74.0060)
        assert update.timezone is None
        assert update.latitude == 40.7128
        assert update.longitude == -74.0060


# =============================================================================
# QUOTE RESPONSE SCHEMA TESTS
# =============================================================================

class TestTodayQuoteResponse:
    """Test TodayQuoteResponse schema"""

    def test_pending_status(self):
        """Should create valid pending response"""
        from app.quotes.schemas import TodayQuoteResponse, QuoteStatus

        response = TodayQuoteResponse(
            has_quote=False,
            status=QuoteStatus.PENDING,
            quote=None,
            message="Your quote will arrive later today"
        )

        assert response.has_quote is False
        assert response.status == QuoteStatus.PENDING
        assert response.quote is None
        assert response.message is not None

    def test_delivered_status(self):
        """Should create valid delivered response with quote"""
        from app.quotes.schemas import (
            TodayQuoteResponse, QuoteStatus, QuoteData, QuoteAuthor
        )

        response = TodayQuoteResponse(
            has_quote=True,
            status=QuoteStatus.DELIVERED,
            quote=QuoteData(
                text="Life is beautiful.",
                author=QuoteAuthor(user_id="123", username="author"),
                post_id="456",
                day_key="2026-01-25",
                received_at=datetime(2026, 1, 25, 14, 30, 0)
            ),
            message=None
        )

        assert response.has_quote is True
        assert response.status == QuoteStatus.DELIVERED
        assert response.quote is not None
        assert response.quote.text == "Life is beautiful."

    def test_unavailable_status(self):
        """Should create valid unavailable response"""
        from app.quotes.schemas import TodayQuoteResponse, QuoteStatus

        response = TodayQuoteResponse(
            has_quote=False,
            status=QuoteStatus.UNAVAILABLE,
            quote=None,
            message="No quote available today"
        )

        assert response.has_quote is False
        assert response.status == QuoteStatus.UNAVAILABLE

    def test_delivered_with_missing_author(self):
        """Should create valid response with null author fields"""
        from app.quotes.schemas import (
            TodayQuoteResponse, QuoteStatus, QuoteData, QuoteAuthor
        )

        # Edge case: author has null fields
        response = TodayQuoteResponse(
            has_quote=True,
            status=QuoteStatus.DELIVERED,
            quote=QuoteData(
                text="Anonymous wisdom.",
                author=QuoteAuthor(user_id=None, username=None),
                post_id=None,
                day_key="2026-01-25",
                received_at=datetime(2026, 1, 25, 14, 30, 0)
            ),
            message=None
        )

        assert response.quote.author.user_id is None
        assert response.quote.author.username is None
        assert response.quote.post_id is None

    def test_long_quote_at_max_length(self):
        """Should accept quotes at max length (200 chars)"""
        from app.quotes.schemas import QuoteData, QuoteAuthor

        long_text = "A" * 200
        quote = QuoteData(
            text=long_text,
            author=QuoteAuthor(user_id="123", username="test"),
            day_key="2026-01-25",
            received_at=datetime(2026, 1, 25, 14, 30, 0)
        )

        assert len(quote.text) == 200


class TestQuoteHistoryResponse:
    """Test QuoteHistoryResponse schema"""

    def test_empty_history(self):
        """Should create valid empty history response"""
        from app.quotes.schemas import QuoteHistoryResponse

        response = QuoteHistoryResponse(
            quotes=[],
            total=0,
            skip=0,
            limit=20,
            has_more=False
        )

        assert response.quotes == []
        assert response.total == 0
        assert response.has_more is False

    def test_paginated_history(self):
        """Should create valid paginated history response"""
        from app.quotes.schemas import (
            QuoteHistoryResponse, QuoteHistoryItem, QuoteAuthor
        )

        response = QuoteHistoryResponse(
            quotes=[
                QuoteHistoryItem(
                    text="Quote 1",
                    author=QuoteAuthor(user_id="u1", username="author1"),
                    post_id="p1",
                    day_key="2026-01-24",
                    received_at=datetime(2026, 1, 24, 10, 0, 0)
                ),
                QuoteHistoryItem(
                    text="Quote 2",
                    author=QuoteAuthor(user_id="u2", username="author2"),
                    post_id="p2",
                    day_key="2026-01-23",
                    received_at=datetime(2026, 1, 23, 10, 0, 0)
                )
            ],
            total=50,
            skip=0,
            limit=20,
            has_more=True
        )

        assert len(response.quotes) == 2
        assert response.total == 50
        assert response.has_more is True
        assert response.quotes[0].day_key > response.quotes[1].day_key

    def test_history_item_with_missing_author(self):
        """Should handle history items with null author"""
        from app.quotes.schemas import QuoteHistoryItem, QuoteAuthor

        item = QuoteHistoryItem(
            text="Quote with unknown author",
            author=QuoteAuthor(user_id=None, username=None),
            post_id=None,
            day_key="2026-01-24",
            received_at=datetime(2026, 1, 24, 10, 0, 0)
        )

        assert item.author.user_id is None
        assert item.author.username is None


# =============================================================================
# CRON RESPONSE SCHEMA TESTS
# =============================================================================

class TestCronInitResponse:
    """Test CronInitResponse schema"""

    def test_valid_response(self):
        """Should create valid init response"""
        from app.quotes.schemas import CronInitResponse

        response = CronInitResponse(
            initialized_count=10,
            skipped_count=5,
            error_count=2
        )

        assert response.initialized_count == 10
        assert response.skipped_count == 5
        assert response.error_count == 2

    def test_all_zeros(self):
        """Should handle all zeros"""
        from app.quotes.schemas import CronInitResponse

        response = CronInitResponse(
            initialized_count=0,
            skipped_count=0,
            error_count=0
        )

        assert response.initialized_count == 0


class TestCronPushResponse:
    """Test CronPushResponse schema"""

    def test_valid_response(self):
        """Should create valid push response"""
        from app.quotes.schemas import CronPushResponse

        response = CronPushResponse(
            processed_count=20,
            sent_count=15,
            no_quote_count=3,
            no_tokens_count=1,
            error_count=1
        )

        assert response.processed_count == 20
        assert response.sent_count == 15
        assert response.no_quote_count == 3
        assert response.no_tokens_count == 1
        assert response.error_count == 1

    def test_defaults(self):
        """Should have sensible defaults"""
        from app.quotes.schemas import CronPushResponse

        response = CronPushResponse(
            processed_count=0,
            sent_count=0
        )

        assert response.no_quote_count == 0
        assert response.no_tokens_count == 0
        assert response.error_count == 0

    def test_no_tokens_scenario(self):
        """Should track when quotes saved but no devices to push to"""
        from app.quotes.schemas import CronPushResponse

        response = CronPushResponse(
            processed_count=10,
            sent_count=5,
            no_quote_count=2,
            no_tokens_count=3,
            error_count=0
        )

        assert response.no_tokens_count == 3
        assert response.processed_count == (
            response.sent_count + response.no_quote_count + response.no_tokens_count + response.error_count
        )


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestBuildTodayQuoteResponse:
    """Test build_today_quote_response helper function"""

    def test_builds_pending_response(self):
        """Should build pending response correctly"""
        from app.quotes.schemas import build_today_quote_response, QuoteStatus

        response = build_today_quote_response(
            has_quote=False,
            status=QuoteStatus.PENDING,
            message="Your quote will arrive soon"
        )

        assert response.has_quote is False
        assert response.status == QuoteStatus.PENDING
        assert response.quote is None
        assert response.message == "Your quote will arrive soon"

    def test_builds_delivered_response(self):
        """Should build delivered response with quote data"""
        from app.quotes.schemas import build_today_quote_response, QuoteStatus

        response = build_today_quote_response(
            has_quote=True,
            status=QuoteStatus.DELIVERED,
            quote_data={
                "text": "Test quote",
                "author_user_id": "user123",
                "author_username": "testuser",
                "post_id": "post456",
                "day_key": "2026-01-25",
                "received_at": datetime(2026, 1, 25, 14, 30, 0)
            }
        )

        assert response.has_quote is True
        assert response.quote.text == "Test quote"
        assert response.quote.author.user_id == "user123"
        assert response.quote.author.username == "testuser"

    def test_builds_response_with_null_author(self):
        """Should handle null author fields"""
        from app.quotes.schemas import build_today_quote_response, QuoteStatus

        response = build_today_quote_response(
            has_quote=True,
            status=QuoteStatus.DELIVERED,
            quote_data={
                "text": "Anonymous quote",
                "author_user_id": None,
                "author_username": None,
                "post_id": None,
                "day_key": "2026-01-25",
                "received_at": datetime(2026, 1, 25, 14, 30, 0)
            }
        )

        assert response.quote.author.user_id is None
        assert response.quote.author.username is None


class TestBuildQuoteHistoryItem:
    """Test build_quote_history_item helper function"""

    def test_builds_item_from_document(self):
        """Should build history item from database document"""
        from app.quotes.schemas import build_quote_history_item

        doc = {
            "quote_text": "Test quote",
            "source_author_user_id": "user123",
            "source_author_username": "testuser",
            "source_post_id": "post456",
            "day_key": "2026-01-24",
            "push_sent_at_utc": datetime(2026, 1, 24, 10, 0, 0),
            "created_at_utc": datetime(2026, 1, 24, 6, 0, 0)
        }

        item = build_quote_history_item(doc)

        assert item.text == "Test quote"
        assert item.author.user_id == "user123"
        assert item.day_key == "2026-01-24"
        assert item.received_at == datetime(2026, 1, 24, 10, 0, 0)

    def test_uses_created_at_when_no_push_sent_at(self):
        """Should fall back to created_at_utc when push_sent_at_utc is missing"""
        from app.quotes.schemas import build_quote_history_item

        doc = {
            "quote_text": "Test quote",
            "source_author_user_id": None,
            "source_author_username": None,
            "source_post_id": None,
            "day_key": "2026-01-24",
            "push_sent_at_utc": None,
            "created_at_utc": datetime(2026, 1, 24, 6, 0, 0)
        }

        item = build_quote_history_item(doc)

        assert item.received_at == datetime(2026, 1, 24, 6, 0, 0)
        assert item.author.user_id is None


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test various edge cases for the quote feature"""

    def test_quote_with_special_characters(self):
        """Should handle quotes with special characters"""
        from app.quotes.schemas import QuoteData, QuoteAuthor

        quote = QuoteData(
            text="Life's meaning - isn't it obvious? 'Ask yourself,' he said.",
            author=QuoteAuthor(user_id="123", username="test"),
            day_key="2026-01-25",
            received_at=datetime(2026, 1, 25, 14, 30, 0)
        )

        assert "-" in quote.text
        assert "'" in quote.text

    def test_quote_with_newlines(self):
        """Should handle quotes with newlines"""
        from app.quotes.schemas import QuoteData, QuoteAuthor

        quote = QuoteData(
            text="Line one.\nLine two.\nLine three.",
            author=QuoteAuthor(user_id="123", username="test"),
            day_key="2026-01-25",
            received_at=datetime(2026, 1, 25, 14, 30, 0)
        )

        assert "\n" in quote.text

    def test_empty_quotes_list_pagination(self):
        """Should handle pagination with empty results"""
        from app.quotes.schemas import QuoteHistoryResponse

        response = QuoteHistoryResponse(
            quotes=[],
            total=1,
            skip=20,
            limit=20,
            has_more=False
        )

        assert response.quotes == []
        assert response.has_more is False
