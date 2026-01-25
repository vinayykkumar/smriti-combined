"""
Unit tests for quote extraction utilities.

Tests sentence splitting, text extraction, and quote generation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Mock database connection before importing extraction module
sys.modules['app.database.connection'] = MagicMock()


class TestSplitIntoSentences:
    """Test sentence splitting logic."""

    def test_simple_sentences(self):
        """Should split simple sentences correctly."""
        from app.quotes.extraction import split_into_sentences

        text = "First sentence. Second sentence. Third sentence."
        sentences = split_into_sentences(text)

        assert len(sentences) == 3
        assert sentences[0] == "First sentence."
        assert sentences[1] == "Second sentence."
        assert sentences[2] == "Third sentence."

    def test_exclamation_and_question(self):
        """Should split on exclamation and question marks."""
        from app.quotes.extraction import split_into_sentences

        text = "What a day! How are you? I'm fine."
        sentences = split_into_sentences(text)

        assert len(sentences) == 3
        assert sentences[0] == "What a day!"
        assert sentences[1] == "How are you?"
        assert sentences[2] == "I'm fine."

    def test_preserves_abbreviations(self):
        """Should not split on common abbreviations."""
        from app.quotes.extraction import split_into_sentences

        text = "Dr. Smith went to Mr. Jones. They talked about Inc. rules."
        sentences = split_into_sentences(text)

        assert len(sentences) == 2
        assert "Dr. Smith" in sentences[0]
        assert "Mr. Jones" in sentences[0]

    def test_empty_string(self):
        """Should return empty list for empty string."""
        from app.quotes.extraction import split_into_sentences

        assert split_into_sentences("") == []
        assert split_into_sentences(None) == []

    def test_single_sentence(self):
        """Should handle single sentence without trailing punctuation."""
        from app.quotes.extraction import split_into_sentences

        text = "Just one sentence"
        sentences = split_into_sentences(text)

        assert len(sentences) == 1
        assert sentences[0] == "Just one sentence"


class TestTruncateAtWordBoundary:
    """Test word boundary truncation."""

    def test_short_text_unchanged(self):
        """Text shorter than max length should be unchanged."""
        from app.quotes.extraction import truncate_at_word_boundary

        text = "Short text"
        result = truncate_at_word_boundary(text, 50)
        assert result == "Short text"

    def test_truncates_at_word_boundary(self):
        """Should truncate at word boundary with ellipsis."""
        from app.quotes.extraction import truncate_at_word_boundary

        text = "This is a longer sentence that needs truncation at word boundary"
        result = truncate_at_word_boundary(text, 30)

        assert len(result) <= 30
        assert result.endswith("...")
        assert not result.endswith(" ...")  # No trailing space before ellipsis

    def test_returns_none_if_no_good_boundary(self):
        """Should return None if can't find good truncation point."""
        from app.quotes.extraction import truncate_at_word_boundary

        text = "Verylongwordwithoutanyspaces"
        result = truncate_at_word_boundary(text, 20)

        assert result is None

    def test_strips_trailing_punctuation(self):
        """Should strip trailing punctuation before ellipsis."""
        from app.quotes.extraction import truncate_at_word_boundary

        text = "First part, second part here"
        result = truncate_at_word_boundary(text, 15)

        # Should not end with ",..." but with "..."
        if result:
            assert not result.endswith(",...")


class TestExtractQuoteFromText:
    """Test quote extraction from text."""

    def test_short_text_returned_as_is(self):
        """Text within limit should be returned unchanged."""
        from app.quotes.extraction import extract_quote_from_text

        text = "A short inspiring quote."
        result = extract_quote_from_text(text)
        assert result == text

    def test_text_at_max_length(self):
        """Text exactly at max length should be returned."""
        from app.quotes.extraction import extract_quote_from_text
        from app.quotes.constants import MAX_QUOTE_LENGTH

        text = "x" * MAX_QUOTE_LENGTH
        result = extract_quote_from_text(text)
        assert result == text

    def test_extracts_complete_sentences(self):
        """Should prefer complete sentences when possible."""
        from app.quotes.extraction import extract_quote_from_text
        from app.quotes.constants import MAX_QUOTE_LENGTH

        text = "First sentence here. Second sentence is a bit longer. Third one is the longest of them all."
        result = extract_quote_from_text(text)

        # Should be complete sentences within limit
        assert result is not None
        assert len(result) <= MAX_QUOTE_LENGTH
        # Should not cut mid-sentence
        assert result.endswith(".") or result.endswith("...")

    def test_too_short_returns_none(self):
        """Text shorter than minimum should return None."""
        from app.quotes.extraction import extract_quote_from_text

        text = "Hi"
        result = extract_quote_from_text(text)
        assert result is None

    def test_empty_returns_none(self):
        """Empty text should return None."""
        from app.quotes.extraction import extract_quote_from_text

        assert extract_quote_from_text("") is None
        assert extract_quote_from_text(None) is None
        assert extract_quote_from_text("   ") is None

    def test_whitespace_normalized(self):
        """Should normalize excessive whitespace."""
        from app.quotes.extraction import extract_quote_from_text

        text = "This   has   multiple   spaces."
        result = extract_quote_from_text(text)
        assert "   " not in result

    def test_long_single_sentence_truncated(self):
        """Very long sentence should be truncated at word boundary."""
        from app.quotes.extraction import extract_quote_from_text
        from app.quotes.constants import MAX_QUOTE_LENGTH

        text = "This is a very long sentence that goes on and on and keeps going without any punctuation and it just continues forever until it exceeds the maximum quote length that we have defined and then some more words to make it even longer than the limit"
        result = extract_quote_from_text(text)

        assert result is not None
        assert len(result) <= MAX_QUOTE_LENGTH
        assert result.endswith("...")

    def test_multiple_sentences_fit(self):
        """Multiple short sentences should be combined."""
        from app.quotes.extraction import extract_quote_from_text

        text = "First. Second. Third. Fourth."
        result = extract_quote_from_text(text)

        assert result is not None
        # Should include multiple sentences
        assert result.count(".") >= 2


class TestPickRandomQuote:
    """Test database quote picking with mocked database."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        mock = MagicMock()
        mock.posts = MagicMock()
        return mock

    @pytest.mark.asyncio
    async def test_returns_none_when_no_posts(self):
        """Should return None when no posts exist."""
        with patch('app.quotes.extraction.get_database') as mock_get_db:
            from app.quotes.extraction import pick_random_quote

            mock_db = MagicMock()
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_db.posts.aggregate = MagicMock(return_value=mock_cursor)
            mock_get_db.return_value = mock_db

            result = await pick_random_quote()

            assert result is None

    @pytest.mark.asyncio
    async def test_returns_quote_from_single_post(self):
        """Should extract quote from a single post."""
        with patch('app.quotes.extraction.get_database') as mock_get_db:
            from app.quotes.extraction import pick_random_quote

            mock_db = MagicMock()
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {
                    "_id": "post123",
                    "title": "A great thought",
                    "text_content": "Life is beautiful when you appreciate the small things.",
                    "author": {
                        "user_id": "user456",
                        "username": "thinker"
                    }
                }
            ])
            mock_db.posts.aggregate = MagicMock(return_value=mock_cursor)
            mock_get_db.return_value = mock_db

            result = await pick_random_quote()

            assert result is not None
            assert "quote_text" in result
            assert result["post_id"] == "post123"
            assert result["author_user_id"] == "user456"
            assert result["author_username"] == "thinker"

    @pytest.mark.asyncio
    async def test_returns_quote_from_multiple_posts(self):
        """Should return quote from one of multiple posts."""
        with patch('app.quotes.extraction.get_database') as mock_get_db:
            from app.quotes.extraction import pick_random_quote

            mock_db = MagicMock()
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {
                    "_id": "post1",
                    "title": "First post",
                    "text_content": "Content of first post.",
                    "author": {"user_id": "u1", "username": "user1"}
                },
                {
                    "_id": "post2",
                    "title": "Second post",
                    "text_content": "Content of second post.",
                    "author": {"user_id": "u2", "username": "user2"}
                },
                {
                    "_id": "post3",
                    "title": "Third post",
                    "text_content": "Content of third post.",
                    "author": {"user_id": "u3", "username": "user3"}
                }
            ])
            mock_db.posts.aggregate = MagicMock(return_value=mock_cursor)
            mock_get_db.return_value = mock_db

            result = await pick_random_quote()

            assert result is not None
            assert result["post_id"] in ["post1", "post2", "post3"]

    @pytest.mark.asyncio
    async def test_skips_posts_with_unusable_text(self):
        """Should skip posts with text that's too short."""
        with patch('app.quotes.extraction.get_database') as mock_get_db:
            from app.quotes.extraction import pick_random_quote

            mock_db = MagicMock()
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {
                    "_id": "bad_post",
                    "title": "Hi",  # Too short
                    "text_content": "",
                    "author": {"user_id": "u1", "username": "user1"}
                },
                {
                    "_id": "good_post",
                    "title": "A meaningful title with substance",
                    "text_content": "And some great content here.",
                    "author": {"user_id": "u2", "username": "user2"}
                }
            ])
            mock_db.posts.aggregate = MagicMock(return_value=mock_cursor)
            mock_get_db.return_value = mock_db

            result = await pick_random_quote()

            assert result is not None
            assert result["post_id"] == "good_post"

    @pytest.mark.asyncio
    async def test_handles_post_with_only_title(self):
        """Should extract quote from post with only title."""
        with patch('app.quotes.extraction.get_database') as mock_get_db:
            from app.quotes.extraction import pick_random_quote

            mock_db = MagicMock()
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {
                    "_id": "title_only",
                    "title": "The best time to plant a tree was 20 years ago.",
                    "text_content": None,
                    "author": {"user_id": "u1", "username": "wisdom"}
                }
            ])
            mock_db.posts.aggregate = MagicMock(return_value=mock_cursor)
            mock_get_db.return_value = mock_db

            result = await pick_random_quote()

            assert result is not None
            assert "plant a tree" in result["quote_text"]

    @pytest.mark.asyncio
    async def test_handles_post_with_only_content(self):
        """Should extract quote from post with only text_content."""
        with patch('app.quotes.extraction.get_database') as mock_get_db:
            from app.quotes.extraction import pick_random_quote

            mock_db = MagicMock()
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {
                    "_id": "content_only",
                    "title": "",
                    "text_content": "Be yourself; everyone else is already taken.",
                    "author": {"user_id": "u1", "username": "oscar"}
                }
            ])
            mock_db.posts.aggregate = MagicMock(return_value=mock_cursor)
            mock_get_db.return_value = mock_db

            result = await pick_random_quote()

            assert result is not None
            assert "Be yourself" in result["quote_text"]
