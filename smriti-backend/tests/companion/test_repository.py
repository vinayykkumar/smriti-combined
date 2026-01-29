"""
Unit tests for Companion repository - conversation history storage.

Tests:
- Settings CRUD operations
- Conversation history storage
- History pagination
- History cleanup
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.companion.repository import CompanionRepository
from app.companion.schemas import (
    CompanionSettings,
    CompanionSettingsUpdate,
    ConversationEntryCreate
)

# Valid ObjectId for testing
TEST_USER_ID = str(ObjectId())


class TestCompanionSettingsRepository:
    """Test settings operations"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = MagicMock()
        db.users = AsyncMock()
        db.companion_history = AsyncMock()
        db.posts = AsyncMock()
        return db

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock db"""
        return CompanionRepository(mock_db)

    @pytest.mark.asyncio
    async def test_get_settings_returns_none_when_not_found(self, repository, mock_db):
        """Test that get_settings returns None when user has no settings"""
        mock_db.users.find_one = AsyncMock(return_value=None)

        result = await repository.get_settings(TEST_USER_ID)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_settings_returns_settings_when_found(self, repository, mock_db):
        """Test that get_settings returns CompanionSettings when found"""
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {
                "opt_in_reflection_analysis": True,
                "preferred_guidance_type": "breath-focus",
                "preferred_tts_voice": "nova",
                "default_meditation_duration": 15,
                "show_guidance_text": True
            }
        })

        result = await repository.get_settings(TEST_USER_ID)

        assert isinstance(result, CompanionSettings)
        assert result.opt_in_reflection_analysis == True
        assert result.preferred_guidance_type == "breath-focus"

    @pytest.mark.asyncio
    async def test_create_default_settings(self, repository, mock_db):
        """Test creating default settings"""
        mock_db.users.update_one = AsyncMock()

        result = await repository.create_default_settings(TEST_USER_ID)

        assert isinstance(result, CompanionSettings)
        assert result.opt_in_reflection_analysis == False
        assert result.preferred_guidance_type == "breath-focus"
        mock_db.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_settings_partial(self, repository, mock_db):
        """Test partial settings update"""
        # First call returns existing settings
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {
                "opt_in_reflection_analysis": False,
                "preferred_guidance_type": "breath-focus",
                "preferred_tts_voice": "nova",
                "default_meditation_duration": 10,
                "show_guidance_text": True
            }
        })
        mock_db.users.update_one = AsyncMock()

        update = CompanionSettingsUpdate(opt_in_reflection_analysis=True)
        result = await repository.update_settings(TEST_USER_ID, update)

        mock_db.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_opt_in_status_true(self, repository, mock_db):
        """Test get_opt_in_status returns True when opted in"""
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {"opt_in_reflection_analysis": True}
        })

        result = await repository.get_opt_in_status(TEST_USER_ID)

        assert result == True

    @pytest.mark.asyncio
    async def test_get_opt_in_status_false_when_not_set(self, repository, mock_db):
        """Test get_opt_in_status returns False when not set"""
        mock_db.users.find_one = AsyncMock(return_value=None)

        result = await repository.get_opt_in_status(TEST_USER_ID)

        assert result == False


class AsyncIterator:
    """Helper class for async iteration in mocks"""
    def __init__(self, items):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


class TestConversationHistoryRepository:
    """Test conversation history operations"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = MagicMock()
        db.users = AsyncMock()
        db.companion_history = AsyncMock()
        db.posts = AsyncMock()
        return db

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock db"""
        return CompanionRepository(mock_db)

    @pytest.mark.asyncio
    async def test_add_history_entry(self, repository, mock_db):
        """Test adding a history entry"""
        inserted_id = ObjectId()
        mock_db.companion_history.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=inserted_id)
        )

        entry = ConversationEntryCreate(
            user_id=TEST_USER_ID,
            type="prompt",
            request={"mood": "peaceful"},
            response={"prompt": "What brings you peace?"}
        )

        result = await repository.add_history_entry(entry)

        assert result.user_id == TEST_USER_ID
        assert result.type == "prompt"
        assert result.id == str(inserted_id)
        mock_db.companion_history.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_history_pagination(self, repository, mock_db):
        """Test paginated history retrieval"""
        mock_db.companion_history.count_documents = AsyncMock(return_value=50)

        # Mock cursor with proper async iteration
        test_docs = [
            {
                "_id": ObjectId(),
                "user_id": TEST_USER_ID,
                "type": "prompt",
                "request": {},
                "response": {},
                "created_at": datetime.now(timezone.utc)
            }
        ]

        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)

        # Make it async iterable
        async def async_iter():
            for doc in test_docs:
                yield doc

        mock_cursor.__aiter__ = lambda self: async_iter()

        mock_db.companion_history.find = MagicMock(return_value=mock_cursor)

        entries, total = await repository.get_history(
            user_id=TEST_USER_ID,
            page=2,
            limit=20
        )

        assert total == 50
        mock_cursor.skip.assert_called_with(20)  # page 2, skip 20

    @pytest.mark.asyncio
    async def test_delete_history_entry(self, repository, mock_db):
        """Test deleting a specific history entry"""
        entry_id = str(ObjectId())
        mock_db.companion_history.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=1)
        )

        result = await repository.delete_history_entry(entry_id, TEST_USER_ID)

        assert result == True
        mock_db.companion_history.delete_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_history_entry_not_found(self, repository, mock_db):
        """Test deleting non-existent entry returns False"""
        entry_id = str(ObjectId())
        mock_db.companion_history.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=0)
        )

        result = await repository.delete_history_entry(entry_id, TEST_USER_ID)

        assert result == False

    @pytest.mark.asyncio
    async def test_delete_all_history(self, repository, mock_db):
        """Test deleting all history for a user"""
        mock_db.companion_history.delete_many = AsyncMock(
            return_value=MagicMock(deleted_count=25)
        )

        result = await repository.delete_all_history(TEST_USER_ID)

        assert result == 25
        mock_db.companion_history.delete_many.assert_called_with({"user_id": TEST_USER_ID})

    @pytest.mark.asyncio
    async def test_cleanup_old_history(self, repository, mock_db):
        """Test cleaning up old history entries"""
        mock_db.companion_history.delete_many = AsyncMock(
            return_value=MagicMock(deleted_count=10)
        )

        result = await repository.cleanup_old_history(retention_days=30)

        assert result == 10
        mock_db.companion_history.delete_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_enforce_max_entries(self, repository, mock_db):
        """Test enforcing maximum entries per user"""
        # User has 250 entries, max is 200
        mock_db.companion_history.count_documents = AsyncMock(return_value=250)

        # Mock finding oldest 50 entries with proper async iteration
        test_ids = [{"_id": ObjectId()} for _ in range(50)]

        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)

        async def async_iter():
            for doc in test_ids:
                yield doc

        mock_cursor.__aiter__ = lambda self: async_iter()

        mock_db.companion_history.find = MagicMock(return_value=mock_cursor)

        mock_db.companion_history.delete_many = AsyncMock(
            return_value=MagicMock(deleted_count=50)
        )

        result = await repository.enforce_max_entries(TEST_USER_ID, max_entries=200)

        assert result == 50

    @pytest.mark.asyncio
    async def test_enforce_max_entries_under_limit(self, repository, mock_db):
        """Test that no deletion happens when under limit"""
        mock_db.companion_history.count_documents = AsyncMock(return_value=100)

        result = await repository.enforce_max_entries(TEST_USER_ID, max_entries=200)

        assert result == 0
        mock_db.companion_history.delete_many.assert_not_called()


class TestUserPostsForContext:
    """Test fetching user posts for AI context"""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.users = AsyncMock()
        db.companion_history = AsyncMock()
        db.posts = AsyncMock()
        return db

    @pytest.fixture
    def repository(self, mock_db):
        return CompanionRepository(mock_db)

    @pytest.mark.asyncio
    async def test_get_user_posts_for_context(self, repository, mock_db):
        """Test fetching user posts for context"""
        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[
            {"content": "I am grateful today", "created_at": datetime.now(timezone.utc)},
            {"content": "Finding peace in the moment", "created_at": datetime.now(timezone.utc)}
        ])

        mock_db.posts.find = MagicMock(return_value=mock_cursor)

        result = await repository.get_user_posts_for_context(TEST_USER_ID, limit=10)

        assert len(result) == 2
        assert result[0]["content"] == "I am grateful today"


# Run tests with: pytest tests/companion/test_repository.py -v
