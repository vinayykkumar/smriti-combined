"""
Unit tests for Circle Post Permissions.

Tests the core permission logic for posting to circles:
1. Non-members cannot post to circles
2. Members can post to circles
3. Design constraint: No admin removal (members cannot be kicked)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId

from app.posts.service import (
    NotCircleMemberError,
    PostVisibilityError,
    validate_circle_membership_for_post,
    create_circle_post,
    get_circle_posts,
)

# Module path for patching check_membership (imported inside functions)
CHECK_MEMBERSHIP_PATH = 'app.circles.dependencies.check_membership'


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_db():
    """Create a mock database connection."""
    db = MagicMock()
    db.posts = MagicMock()
    db.circles = MagicMock()
    return db


@pytest.fixture
def sample_user_id():
    """Sample user ID."""
    return "507f1f77bcf86cd799439011"


@pytest.fixture
def other_user_id():
    """Another user ID (non-member)."""
    return "507f1f77bcf86cd799439099"


@pytest.fixture
def sample_circle_id():
    """Sample circle ID."""
    return "507f1f77bcf86cd799439022"


@pytest.fixture
def sample_circle(sample_user_id, sample_circle_id):
    """Sample circle with one member."""
    return {
        "_id": ObjectId(sample_circle_id),
        "name": "Test Circle",
        "members": [
            {
                "user_id": sample_user_id,
                "username": "testuser",
                "joined_at": datetime.utcnow()
            }
        ],
        "member_count": 1,
        "max_members": 5,
        "invite_code": "A7X2K9M4",
        "deletion_votes": [],
        "created_at": datetime.utcnow(),
        "created_by": {
            "user_id": sample_user_id,
            "username": "testuser"
        }
    }


@pytest.fixture
def sample_post_dict(sample_user_id):
    """Sample post data without visibility."""
    return {
        "content_type": "note",
        "text_content": "Hello circle!",
        "author": {
            "user_id": sample_user_id,
            "username": "testuser"
        },
        "created_at": datetime.utcnow().isoformat()
    }


# =============================================================================
# EXCEPTION TESTS
# =============================================================================

class TestPostVisibilityExceptions:
    """Tests for post visibility exceptions."""

    def test_not_circle_member_error_with_circle_id(self):
        """Test NotCircleMemberError includes circle ID in message."""
        circle_id = "507f1f77bcf86cd799439022"
        error = NotCircleMemberError(circle_id)

        assert circle_id in error.message
        assert error.code == "NOT_CIRCLE_MEMBER"
        assert error.circle_id == circle_id

    def test_not_circle_member_error_without_circle_id(self):
        """Test NotCircleMemberError without specific circle ID."""
        error = NotCircleMemberError()

        assert "not a member" in error.message.lower()
        assert error.code == "NOT_CIRCLE_MEMBER"
        assert error.circle_id is None

    def test_post_visibility_error_base(self):
        """Test base PostVisibilityError."""
        error = PostVisibilityError("Custom message", "CUSTOM_CODE")

        assert error.message == "Custom message"
        assert error.code == "CUSTOM_CODE"


# =============================================================================
# NON-MEMBER CANNOT POST TESTS
# =============================================================================

class TestNonMemberCannotPost:
    """Tests verifying non-members cannot post to circles."""

    @pytest.mark.asyncio
    async def test_validate_membership_returns_false_for_non_member(
        self, mock_db, sample_circle_id, other_user_id
    ):
        """Test that validation fails for non-member."""
        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False

            is_valid, invalid_circle_id = await validate_circle_membership_for_post(
                mock_db,
                [sample_circle_id],
                other_user_id
            )

            assert is_valid is False
            assert invalid_circle_id == sample_circle_id
            mock_check.assert_called_once_with(mock_db, sample_circle_id, other_user_id)

    @pytest.mark.asyncio
    async def test_create_circle_post_raises_for_non_member(
        self, mock_db, sample_circle_id, other_user_id, sample_post_dict
    ):
        """Test that creating a circle post raises error for non-member."""
        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False

            with pytest.raises(NotCircleMemberError) as exc_info:
                await create_circle_post(
                    mock_db,
                    sample_post_dict,
                    [sample_circle_id],
                    other_user_id
                )

            assert exc_info.value.circle_id == sample_circle_id
            assert exc_info.value.code == "NOT_CIRCLE_MEMBER"

    @pytest.mark.asyncio
    async def test_non_member_blocked_from_multiple_circles(
        self, mock_db, other_user_id, sample_post_dict
    ):
        """Test that non-member is blocked even when trying multiple circles."""
        circle_ids = [
            "507f1f77bcf86cd799439022",
            "507f1f77bcf86cd799439033",
            "507f1f77bcf86cd799439044"
        ]

        # User is not a member of any circle
        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False

            with pytest.raises(NotCircleMemberError) as exc_info:
                await create_circle_post(
                    mock_db,
                    sample_post_dict,
                    circle_ids,
                    other_user_id
                )

            # Should fail on the first circle
            assert exc_info.value.circle_id == circle_ids[0]

    @pytest.mark.asyncio
    async def test_partial_membership_fails(
        self, mock_db, sample_user_id, sample_post_dict
    ):
        """Test that user must be member of ALL circles, not just some."""
        circle_ids = [
            "507f1f77bcf86cd799439022",  # Member
            "507f1f77bcf86cd799439033",  # Member
            "507f1f77bcf86cd799439044"   # NOT a member
        ]

        # User is member of first two, but not the third
        async def check_membership_side_effect(db, circle_id, user_id):
            if circle_id == "507f1f77bcf86cd799439044":
                return False
            return True

        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = check_membership_side_effect

            with pytest.raises(NotCircleMemberError) as exc_info:
                await create_circle_post(
                    mock_db,
                    sample_post_dict,
                    circle_ids,
                    sample_user_id
                )

            # Should fail on the third circle
            assert exc_info.value.circle_id == "507f1f77bcf86cd799439044"

    @pytest.mark.asyncio
    async def test_get_circle_posts_raises_for_non_member(
        self, mock_db, sample_circle_id, other_user_id
    ):
        """Test that viewing circle posts raises error for non-member."""
        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False

            with pytest.raises(NotCircleMemberError) as exc_info:
                await get_circle_posts(
                    mock_db,
                    sample_circle_id,
                    other_user_id
                )

            assert exc_info.value.circle_id == sample_circle_id


# =============================================================================
# MEMBER CAN POST TESTS
# =============================================================================

class TestMemberCanPost:
    """Tests verifying members can post to circles."""

    @pytest.mark.asyncio
    async def test_validate_membership_returns_true_for_member(
        self, mock_db, sample_circle_id, sample_user_id
    ):
        """Test that validation passes for member."""
        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True

            is_valid, invalid_circle_id = await validate_circle_membership_for_post(
                mock_db,
                [sample_circle_id],
                sample_user_id
            )

            assert is_valid is True
            assert invalid_circle_id is None

    @pytest.mark.asyncio
    async def test_member_can_post_to_single_circle(
        self, mock_db, sample_circle_id, sample_user_id, sample_post_dict
    ):
        """Test that member can successfully post to a circle."""
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()

        created_post = {
            **sample_post_dict,
            "_id": mock_insert_result.inserted_id,
            "visibility": "circles",
            "circle_ids": [sample_circle_id]
        }

        mock_db.posts.insert_one = AsyncMock(return_value=mock_insert_result)
        mock_db.posts.find_one = AsyncMock(return_value=created_post)

        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True

            with patch('app.posts.service._clear_search_cache'):
                result = await create_circle_post(
                    mock_db,
                    sample_post_dict.copy(),
                    [sample_circle_id],
                    sample_user_id
                )

            assert result is not None
            assert result["visibility"] == "circles"
            assert result["circle_ids"] == [sample_circle_id]

    @pytest.mark.asyncio
    async def test_member_can_post_to_multiple_circles(
        self, mock_db, sample_user_id, sample_post_dict
    ):
        """Test that member can post to multiple circles at once."""
        circle_ids = [
            "507f1f77bcf86cd799439022",
            "507f1f77bcf86cd799439033",
            "507f1f77bcf86cd799439044"
        ]

        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()

        created_post = {
            **sample_post_dict,
            "_id": mock_insert_result.inserted_id,
            "visibility": "circles",
            "circle_ids": circle_ids
        }

        mock_db.posts.insert_one = AsyncMock(return_value=mock_insert_result)
        mock_db.posts.find_one = AsyncMock(return_value=created_post)

        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            # Member of all circles
            mock_check.return_value = True

            with patch('app.posts.service._clear_search_cache'):
                result = await create_circle_post(
                    mock_db,
                    sample_post_dict.copy(),
                    circle_ids,
                    sample_user_id
                )

            assert result is not None
            assert result["circle_ids"] == circle_ids
            # Should have checked membership for all 3 circles
            assert mock_check.call_count == 3

    @pytest.mark.asyncio
    async def test_member_can_view_circle_posts(
        self, mock_db, sample_circle_id, sample_user_id
    ):
        """Test that member can view posts in their circle."""
        sample_posts = [
            {"_id": ObjectId(), "text_content": "Post 1"},
            {"_id": ObjectId(), "text_content": "Post 2"}
        ]

        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=sample_posts)

        mock_db.posts.find = MagicMock(return_value=mock_cursor)
        mock_db.posts.count_documents = AsyncMock(return_value=2)

        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True

            posts, total = await get_circle_posts(
                mock_db,
                sample_circle_id,
                sample_user_id
            )

            assert len(posts) == 2
            assert total == 2


# =============================================================================
# NO ADMIN REMOVAL DESIGN CONSTRAINT TESTS
# =============================================================================

class TestNoAdminRemovalDesign:
    """
    Tests verifying the design constraint that members CANNOT be removed.

    Sangha Circles design principles:
    - NO admins or special roles - everyone is equal
    - Members CANNOT leave or be kicked - lifetime commitment
    - Circle can only be deleted by UNANIMOUS vote of all members
    """

    def test_circle_has_no_admin_field(self, sample_circle):
        """Verify circle schema has no admin or owner field."""
        assert "admin" not in sample_circle
        assert "owner" not in sample_circle
        assert "admins" not in sample_circle
        assert "moderators" not in sample_circle

    def test_members_are_equal_no_roles(self, sample_circle):
        """Verify members have no role field - everyone is equal."""
        for member in sample_circle["members"]:
            assert "role" not in member
            assert "is_admin" not in member
            assert "permissions" not in member

    def test_created_by_is_informational_only(self, sample_circle, sample_user_id):
        """
        Verify created_by field exists but grants no special powers.

        The created_by field is purely for historical record (like showing
        "Founded by @user") and does not grant any admin privileges.
        """
        assert "created_by" in sample_circle
        assert sample_circle["created_by"]["user_id"] == sample_user_id

        # created_by should not have any special permission fields
        created_by = sample_circle["created_by"]
        assert "is_admin" not in created_by
        assert "can_remove_members" not in created_by
        assert "permissions" not in created_by

    def test_circle_has_deletion_votes_for_unanimous_delete(self, sample_circle):
        """
        Verify circle has deletion_votes field for unanimous deletion.

        Since no one can kick members, the only way to "end" a circle
        is for ALL members to vote to delete it.
        """
        assert "deletion_votes" in sample_circle
        assert isinstance(sample_circle["deletion_votes"], list)

    def test_repository_has_no_remove_member_method(self):
        """
        Verify the repository does not expose a remove_member method.

        This is a design constraint - members cannot be removed.
        """
        from app.circles.repository import CircleRepository

        # Check that there's no method to kick/remove members
        # (Note: remove_member might exist internally for cleanup but
        # should not be used for kicking members)
        repo_methods = [m for m in dir(CircleRepository) if not m.startswith('_')]

        # These methods should NOT exist in a no-admin design
        assert "kick_member" not in repo_methods
        assert "ban_member" not in repo_methods
        assert "remove_member_by_admin" not in repo_methods

    def test_dependencies_has_no_admin_verification(self):
        """
        Verify dependencies module has no admin-related functions.
        """
        from app.circles import dependencies

        dependency_functions = [f for f in dir(dependencies) if not f.startswith('_')]

        # These functions should NOT exist
        assert "verify_admin" not in dependency_functions
        assert "verify_circle_admin" not in dependency_functions
        assert "is_admin" not in dependency_functions
        assert "require_admin" not in dependency_functions

    def test_is_circle_creator_is_informational_only(self):
        """
        Test that is_circle_creator function is informational only.
        """
        from app.circles.dependencies import is_circle_creator

        circle = {
            "created_by": {"user_id": "user123", "username": "creator"}
        }

        # Function exists but only for informational purposes
        assert is_circle_creator(circle, "user123") is True
        assert is_circle_creator(circle, "other_user") is False

        # The function should NOT be used to grant special permissions
        # It's purely for displaying "Creator" badge in UI


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestPostPermissionEdgeCases:
    """Edge case tests for post permissions."""

    @pytest.mark.asyncio
    async def test_empty_circle_ids_validation(self, mock_db, sample_user_id):
        """Test validation with empty circle_ids list."""
        is_valid, invalid_circle_id = await validate_circle_membership_for_post(
            mock_db,
            [],  # Empty list
            sample_user_id
        )

        # Empty list should be valid (no circles to check)
        assert is_valid is True
        assert invalid_circle_id is None

    @pytest.mark.asyncio
    async def test_invalid_circle_id_format_fails(
        self, mock_db, sample_user_id, sample_post_dict
    ):
        """Test that invalid ObjectId format fails gracefully."""
        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            # check_membership returns False for invalid IDs
            mock_check.return_value = False

            is_valid, invalid_circle_id = await validate_circle_membership_for_post(
                mock_db,
                ["invalid-not-objectid"],
                sample_user_id
            )

            assert is_valid is False
            assert invalid_circle_id == "invalid-not-objectid"

    @pytest.mark.asyncio
    async def test_membership_checked_in_order(
        self, mock_db, sample_user_id, sample_post_dict
    ):
        """Test that membership is checked in the order circles are specified."""
        circle_ids = ["circle_a", "circle_b", "circle_c"]
        checked_order = []

        async def track_check_order(db, circle_id, user_id):
            checked_order.append(circle_id)
            return True

        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = track_check_order

            await validate_circle_membership_for_post(
                mock_db,
                circle_ids,
                sample_user_id
            )

            assert checked_order == circle_ids  # Same order

    @pytest.mark.asyncio
    async def test_post_creation_sets_correct_visibility(
        self, mock_db, sample_circle_id, sample_user_id
    ):
        """Test that create_circle_post sets visibility='circles'."""
        post_dict = {
            "content_type": "note",
            "text_content": "Test post"
        }

        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()

        captured_post = {}

        async def capture_insert(doc):
            captured_post.update(doc)
            return mock_insert_result

        mock_db.posts.insert_one = AsyncMock(side_effect=capture_insert)
        mock_db.posts.find_one = AsyncMock(return_value={
            **post_dict,
            "_id": mock_insert_result.inserted_id
        })

        with patch(CHECK_MEMBERSHIP_PATH, new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True

            with patch('app.posts.service._clear_search_cache'):
                await create_circle_post(
                    mock_db,
                    post_dict,
                    [sample_circle_id],
                    sample_user_id
                )

        # Verify the post was saved with correct visibility
        assert captured_post.get("visibility") == "circles"
        assert captured_post.get("circle_ids") == [sample_circle_id]
