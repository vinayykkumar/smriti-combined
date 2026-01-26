"""
Unit tests for Circle schemas.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.circles.schemas import (
    CircleCreate,
    CircleJoin,
    CircleUpdate,
    CircleMember,
    CircleCreator,
    CirclePreview,
    CircleDeleteVoteResponse,
    Visibility,
)
from app.circles.constants import (
    MIN_CIRCLE_NAME_LENGTH,
    MAX_CIRCLE_NAME_LENGTH,
    MAX_CIRCLE_DESCRIPTION_LENGTH,
    CIRCLE_COLORS,
)


class TestCircleCreate:
    """Tests for CircleCreate schema."""

    def test_valid_circle_create_minimal(self):
        """Test creating circle with just a name."""
        data = {"name": "Friends"}
        circle = CircleCreate(**data)
        assert circle.name == "Friends"
        assert circle.description is None
        assert circle.color is None
        assert circle.emoji is None

    def test_valid_circle_create_full(self):
        """Test creating circle with all fields."""
        data = {
            "name": "College Friends",
            "description": "Our little corner",
            "color": "#7986CB",
            "emoji": "🎓"
        }
        circle = CircleCreate(**data)
        assert circle.name == "College Friends"
        assert circle.description == "Our little corner"
        assert circle.color == "#7986CB"
        assert circle.emoji == "🎓"

    def test_name_too_short(self):
        """Test that name must be at least MIN_CIRCLE_NAME_LENGTH chars."""
        data = {"name": "A"}  # Too short
        with pytest.raises(ValidationError) as exc_info:
            CircleCreate(**data)
        assert "at least" in str(exc_info.value).lower() or "min_length" in str(exc_info.value).lower()

    def test_name_too_long(self):
        """Test that name cannot exceed MAX_CIRCLE_NAME_LENGTH chars."""
        data = {"name": "A" * (MAX_CIRCLE_NAME_LENGTH + 1)}
        with pytest.raises(ValidationError):
            CircleCreate(**data)

    def test_name_gets_stripped(self):
        """Test that name whitespace is trimmed."""
        data = {"name": "  Friends  "}
        circle = CircleCreate(**data)
        assert circle.name == "Friends"

    def test_description_too_long(self):
        """Test that description cannot exceed max length."""
        data = {
            "name": "Friends",
            "description": "A" * (MAX_CIRCLE_DESCRIPTION_LENGTH + 1)
        }
        with pytest.raises(ValidationError):
            CircleCreate(**data)

    def test_empty_description_becomes_none(self):
        """Test that empty description is converted to None."""
        data = {"name": "Friends", "description": "   "}
        circle = CircleCreate(**data)
        assert circle.description is None

    def test_invalid_color_rejected(self):
        """Test that color must be from the allowed palette."""
        data = {"name": "Friends", "color": "#FFFFFF"}
        with pytest.raises(ValidationError) as exc_info:
            CircleCreate(**data)
        assert "palette" in str(exc_info.value).lower()

    def test_valid_color_accepted(self):
        """Test that valid palette colors are accepted."""
        for color in CIRCLE_COLORS[:3]:  # Test first 3 colors
            data = {"name": "Friends", "color": color}
            circle = CircleCreate(**data)
            assert circle.color == color.upper()

    def test_color_normalized_to_uppercase(self):
        """Test that color is normalized to uppercase."""
        data = {"name": "Friends", "color": "#7986cb"}  # lowercase
        circle = CircleCreate(**data)
        assert circle.color == "#7986CB"


class TestCircleJoin:
    """Tests for CircleJoin schema."""

    def test_valid_invite_code(self):
        """Test valid 8-char invite code."""
        data = {"inviteCode": "A7X2K9M4"}
        join = CircleJoin(**data)
        assert join.invite_code == "A7X2K9M4"

    def test_invite_code_normalized_to_uppercase(self):
        """Test that invite code is uppercased."""
        data = {"inviteCode": "a7x2k9m4"}
        join = CircleJoin(**data)
        assert join.invite_code == "A7X2K9M4"

    def test_invite_code_spaces_removed(self):
        """Test that spaces in invite code are removed."""
        data = {"inviteCode": "A7X2 K9M4"}
        join = CircleJoin(**data)
        assert join.invite_code == "A7X2K9M4"

    def test_invite_code_too_short(self):
        """Test that invite code must be 8 chars."""
        data = {"inviteCode": "A7X2K"}
        with pytest.raises(ValidationError):
            CircleJoin(**data)

    def test_invite_code_too_long(self):
        """Test that invite code cannot exceed 8 chars."""
        data = {"inviteCode": "A7X2K9M4XX"}
        with pytest.raises(ValidationError):
            CircleJoin(**data)


class TestCircleUpdate:
    """Tests for CircleUpdate schema."""

    def test_empty_update(self):
        """Test update with no fields."""
        update = CircleUpdate()
        assert not update.has_updates()

    def test_partial_update(self):
        """Test update with only some fields."""
        update = CircleUpdate(name="New Name")
        assert update.has_updates()
        assert update.name == "New Name"
        assert update.description is None

    def test_full_update(self):
        """Test update with all fields."""
        update = CircleUpdate(
            name="New Name",
            description="New desc",
            color="#7986CB",
            emoji="🌸"
        )
        assert update.has_updates()

    def test_invalid_color_in_update(self):
        """Test that invalid color is rejected in update."""
        with pytest.raises(ValidationError):
            CircleUpdate(color="#FFFFFF")


class TestCircleMember:
    """Tests for CircleMember schema."""

    def test_valid_member(self):
        """Test creating a valid member."""
        member = CircleMember(
            userId="507f1f77bcf86cd799439011",
            username="testuser"
        )
        assert member.user_id == "507f1f77bcf86cd799439011"
        assert member.username == "testuser"
        assert member.joined_at is not None

    def test_member_with_alias(self):
        """Test that alias works for user_id."""
        data = {"userId": "123", "username": "test"}
        member = CircleMember(**data)
        assert member.user_id == "123"


class TestCirclePreview:
    """Tests for CirclePreview schema."""

    def test_preview_full_circle(self):
        """Test preview for a full circle."""
        preview = CirclePreview(
            name="Friends",
            color="#7986CB",
            memberCount=5,
            maxMembers=5,
            isFull=True,
            alreadyMember=False,
            createdAt=datetime.utcnow()
        )
        assert preview.is_full is True
        assert preview.already_member is False

    def test_preview_already_member(self):
        """Test preview when user is already a member."""
        preview = CirclePreview(
            name="Friends",
            color="#7986CB",
            memberCount=3,
            maxMembers=5,
            isFull=False,
            alreadyMember=True,
            createdAt=datetime.utcnow()
        )
        assert preview.already_member is True


class TestCircleDeleteVoteResponse:
    """Tests for CircleDeleteVoteResponse schema."""

    def test_vote_response_not_deleted(self):
        """Test vote response when circle is not deleted."""
        response = CircleDeleteVoteResponse(
            votesNeeded=5,
            votesCast=2,
            yourVote=True,
            deleted=False
        )
        assert response.votes_needed == 5
        assert response.votes_cast == 2
        assert response.your_vote is True
        assert response.deleted is False

    def test_vote_response_deleted(self):
        """Test vote response when circle is deleted."""
        response = CircleDeleteVoteResponse(
            votesNeeded=5,
            votesCast=5,
            yourVote=True,
            deleted=True
        )
        assert response.deleted is True
