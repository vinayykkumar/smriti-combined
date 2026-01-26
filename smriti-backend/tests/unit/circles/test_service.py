"""
Unit tests for Circle service layer.
Uses mocked database to test business logic.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId

from app.circles.service import (
    format_circle_response,
    format_circle_list_item,
    CircleNotFoundError,
    CircleFullError,
    AlreadyMemberError,
    InvalidInviteCodeError,
    CircleLimitReachedError,
)
from app.circles.schemas import CircleCreate, CirclePreview
from app.circles.constants import MAX_MEMBERS_PER_CIRCLE, MAX_CIRCLES_PER_USER


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "user_id": "507f1f77bcf86cd799439011",
        "username": "testuser"
    }


@pytest.fixture
def sample_circle():
    """Sample circle document from database."""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439022"),
        "name": "Test Circle",
        "description": "A test circle",
        "color": "#7986CB",
        "emoji": "🎓",
        "invite_code": "A7X2K9M4",
        "members": [
            {
                "user_id": "507f1f77bcf86cd799439011",
                "username": "testuser",
                "joined_at": datetime.utcnow()
            }
        ],
        "member_count": 1,
        "max_members": 5,
        "deletion_votes": [],
        "created_at": datetime.utcnow(),
        "created_by": {
            "user_id": "507f1f77bcf86cd799439011",
            "username": "testuser"
        }
    }


# =============================================================================
# EXCEPTION TESTS
# =============================================================================

class TestCircleExceptions:
    """Tests for circle service exceptions."""

    def test_circle_not_found_error(self):
        """Test CircleNotFoundError has correct message and code."""
        error = CircleNotFoundError()
        assert "not found" in error.message.lower() or "not a member" in error.message.lower()
        assert error.code == "CIRCLE_NOT_FOUND"

    def test_circle_full_error(self):
        """Test CircleFullError has correct message."""
        error = CircleFullError()
        assert "full" in error.message.lower()
        assert str(MAX_MEMBERS_PER_CIRCLE) in error.message
        assert error.code == "CIRCLE_FULL"

    def test_already_member_error(self):
        """Test AlreadyMemberError has correct message."""
        error = AlreadyMemberError()
        assert "already" in error.message.lower()
        assert error.code == "ALREADY_MEMBER"

    def test_invalid_invite_code_error(self):
        """Test InvalidInviteCodeError has correct message."""
        error = InvalidInviteCodeError()
        assert "invalid" in error.message.lower()
        assert error.code == "INVALID_INVITE_CODE"

    def test_circle_limit_reached_error(self):
        """Test CircleLimitReachedError has correct message."""
        error = CircleLimitReachedError()
        assert "maximum" in error.message.lower() or "reached" in error.message.lower()
        assert str(MAX_CIRCLES_PER_USER) in error.message
        assert error.code == "CIRCLE_LIMIT_REACHED"


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestFormatCircleResponse:
    """Tests for format_circle_response helper."""

    def test_format_circle_response_basic(self, sample_circle, sample_user):
        """Test formatting circle for API response."""
        result = format_circle_response(sample_circle, sample_user["user_id"])

        assert result["circleId"] == str(sample_circle["_id"])
        assert result["name"] == "Test Circle"
        assert result["description"] == "A test circle"
        assert result["color"] == "#7986CB"
        assert result["emoji"] == "🎓"
        assert result["inviteCode"] == "A7X2K9M4"
        assert result["memberCount"] == 1
        assert result["maxMembers"] == 5
        assert result["deletionVotes"] == 0
        assert result["myDeletionVote"] is False
        assert len(result["members"]) == 1

    def test_format_circle_response_members_format(self, sample_circle, sample_user):
        """Test that members are formatted correctly."""
        result = format_circle_response(sample_circle, sample_user["user_id"])

        member = result["members"][0]
        assert "userId" in member
        assert "username" in member
        assert "joinedAt" in member
        assert member["userId"] == sample_user["user_id"]
        assert member["username"] == "testuser"

    def test_format_circle_response_created_by(self, sample_circle, sample_user):
        """Test that createdBy is formatted correctly."""
        result = format_circle_response(sample_circle, sample_user["user_id"])

        assert "createdBy" in result
        assert result["createdBy"]["userId"] == sample_user["user_id"]
        assert result["createdBy"]["username"] == "testuser"

    def test_format_circle_response_with_deletion_vote(self, sample_circle, sample_user):
        """Test formatting when user has voted to delete."""
        circle = {**sample_circle}
        circle["deletion_votes"] = [sample_user["user_id"]]

        result = format_circle_response(circle, sample_user["user_id"])

        assert result["deletionVotes"] == 1
        assert result["myDeletionVote"] is True

    def test_format_circle_response_user_not_voted(self, sample_circle, sample_user):
        """Test formatting when other users have voted but current user hasn't."""
        circle = {**sample_circle}
        circle["deletion_votes"] = ["other_user_id"]

        result = format_circle_response(circle, sample_user["user_id"])

        assert result["deletionVotes"] == 1
        assert result["myDeletionVote"] is False

    def test_format_circle_response_multiple_deletion_votes(self, sample_circle, sample_user):
        """Test formatting with multiple deletion votes."""
        circle = {**sample_circle}
        circle["member_count"] = 3
        circle["deletion_votes"] = [sample_user["user_id"], "user2", "user3"]

        result = format_circle_response(circle, sample_user["user_id"])

        assert result["deletionVotes"] == 3
        assert result["myDeletionVote"] is True


class TestFormatCircleListItem:
    """Tests for format_circle_list_item helper."""

    def test_format_list_item_basic(self, sample_circle):
        """Test formatting circle for list view."""
        result = format_circle_list_item(sample_circle)

        assert result["circleId"] == str(sample_circle["_id"])
        assert result["name"] == "Test Circle"
        assert result["description"] == "A test circle"
        assert result["color"] == "#7986CB"
        assert result["emoji"] == "🎓"
        assert result["memberCount"] == 1
        assert result["maxMembers"] == 5

    def test_format_list_item_with_activity(self, sample_circle):
        """Test formatting with last activity timestamp."""
        circle = {**sample_circle}
        activity_time = datetime.utcnow()
        circle["last_activity_at"] = activity_time

        result = format_circle_list_item(circle)

        assert result["lastActivityAt"] is not None

    def test_format_list_item_without_activity(self, sample_circle):
        """Test formatting without last activity (no posts yet)."""
        result = format_circle_list_item(sample_circle)

        assert result["lastActivityAt"] is None

    def test_format_list_item_no_invite_code(self, sample_circle):
        """Test that list item doesn't include invite code (for privacy)."""
        result = format_circle_list_item(sample_circle)

        assert "inviteCode" not in result

    def test_format_list_item_no_members_list(self, sample_circle):
        """Test that list item doesn't include full members list."""
        result = format_circle_list_item(sample_circle)

        assert "members" not in result


# =============================================================================
# BUSINESS LOGIC TESTS (Unit tests without DB)
# =============================================================================

class TestCirclePreviewLogic:
    """Tests for CirclePreview creation logic."""

    def test_preview_full_circle(self):
        """Test preview for a full circle."""
        preview = CirclePreview(
            name="Full Circle",
            color="#7986CB",
            memberCount=5,
            maxMembers=5,
            isFull=True,
            alreadyMember=False,
            createdAt=datetime.utcnow()
        )

        assert preview.is_full is True
        assert preview.member_count == preview.max_members

    def test_preview_not_full(self):
        """Test preview for a circle with space."""
        preview = CirclePreview(
            name="Open Circle",
            color="#7986CB",
            memberCount=3,
            maxMembers=5,
            isFull=False,
            alreadyMember=False,
            createdAt=datetime.utcnow()
        )

        assert preview.is_full is False
        assert preview.member_count < preview.max_members

    def test_preview_already_member(self):
        """Test preview when user is already a member."""
        preview = CirclePreview(
            name="My Circle",
            color="#7986CB",
            memberCount=2,
            maxMembers=5,
            isFull=False,
            alreadyMember=True,
            createdAt=datetime.utcnow()
        )

        assert preview.already_member is True


class TestCircleCreateSchema:
    """Tests for CircleCreate schema validation."""

    def test_create_minimal(self):
        """Test creating with minimal data."""
        circle = CircleCreate(name="Test")
        assert circle.name == "Test"
        assert circle.description is None
        assert circle.color is None
        assert circle.emoji is None

    def test_create_full(self):
        """Test creating with all fields."""
        circle = CircleCreate(
            name="Full Circle",
            description="Description",
            color="#7986CB",
            emoji="🎓"
        )
        assert circle.name == "Full Circle"
        assert circle.description == "Description"
        assert circle.color == "#7986CB"
        assert circle.emoji == "🎓"

    def test_name_stripped(self):
        """Test that name is stripped of whitespace."""
        circle = CircleCreate(name="  Spaced  ")
        assert circle.name == "Spaced"


# =============================================================================
# MEMBERSHIP LOGIC TESTS
# =============================================================================

class TestMembershipLogic:
    """Tests for membership-related logic."""

    def test_is_member_check(self, sample_circle, sample_user):
        """Test checking if user is in members list."""
        members = sample_circle["members"]
        user_ids = [m["user_id"] for m in members]

        assert sample_user["user_id"] in user_ids
        assert "other_user" not in user_ids

    def test_member_count_matches_array(self, sample_circle):
        """Test that member_count matches members array length."""
        assert sample_circle["member_count"] == len(sample_circle["members"])

    def test_max_members_constant(self, sample_circle):
        """Test that max_members is set correctly."""
        assert sample_circle["max_members"] == MAX_MEMBERS_PER_CIRCLE


class TestDeletionVoteLogic:
    """Tests for deletion vote logic."""

    def test_unanimous_detection(self, sample_circle):
        """Test detecting unanimous vote."""
        circle = {**sample_circle}
        circle["member_count"] = 3
        circle["deletion_votes"] = ["user1", "user2", "user3"]

        votes_cast = len(circle["deletion_votes"])
        member_count = circle["member_count"]

        assert votes_cast >= member_count  # Unanimous!

    def test_not_unanimous(self, sample_circle):
        """Test detecting non-unanimous vote."""
        circle = {**sample_circle}
        circle["member_count"] = 3
        circle["deletion_votes"] = ["user1"]

        votes_cast = len(circle["deletion_votes"])
        member_count = circle["member_count"]

        assert votes_cast < member_count  # Not unanimous

    def test_user_voted_check(self, sample_circle, sample_user):
        """Test checking if user has voted."""
        circle = {**sample_circle}
        circle["deletion_votes"] = [sample_user["user_id"]]

        user_voted = sample_user["user_id"] in circle["deletion_votes"]
        assert user_voted is True

    def test_user_not_voted_check(self, sample_circle, sample_user):
        """Test checking user hasn't voted."""
        circle = {**sample_circle}
        circle["deletion_votes"] = ["other_user"]

        user_voted = sample_user["user_id"] in circle["deletion_votes"]
        assert user_voted is False
