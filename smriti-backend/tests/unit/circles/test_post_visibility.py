"""
Unit tests for Post visibility features (circles integration).
"""
import pytest
from pydantic import ValidationError
from bson import ObjectId

from app.posts.schemas import (
    PostCreate,
    PostInDB,
    ContentType,
    Visibility,
    AuthorSchema,
)


class TestVisibilityEnum:
    """Tests for Visibility enum."""

    def test_visibility_values(self):
        """Test that visibility has expected values."""
        assert Visibility.public == "public"
        assert Visibility.circles == "circles"
        assert Visibility.private == "private"

    def test_visibility_from_string(self):
        """Test creating visibility from string."""
        assert Visibility("public") == Visibility.public
        assert Visibility("circles") == Visibility.circles


class TestPostCreateWithVisibility:
    """Tests for PostCreate with visibility fields."""

    def test_default_visibility_is_public(self):
        """Test that default visibility is public."""
        post = PostCreate(contentType="note", textContent="Hello")
        assert post.visibility == Visibility.public
        assert post.circle_ids is None

    def test_public_post_without_circles(self):
        """Test creating public post without circle_ids."""
        post = PostCreate(
            contentType="note",
            textContent="Hello world",
            visibility="public"
        )
        assert post.visibility == Visibility.public
        assert post.circle_ids is None

    def test_public_post_with_empty_circles_fails(self):
        """Test that public post with circle_ids fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            PostCreate(
                contentType="note",
                textContent="Hello",
                visibility="public",
                circleIds=["507f1f77bcf86cd799439011"]
            )
        assert "circle_ids must be empty" in str(exc_info.value).lower()

    def test_circles_post_requires_circle_ids(self):
        """Test that circles visibility requires circle_ids."""
        with pytest.raises(ValidationError) as exc_info:
            PostCreate(
                contentType="note",
                textContent="Hello",
                visibility="circles"
            )
        assert "circle_ids is required" in str(exc_info.value).lower()

    def test_circles_post_with_empty_array_fails(self):
        """Test that circles post with empty circle_ids fails."""
        with pytest.raises(ValidationError) as exc_info:
            PostCreate(
                contentType="note",
                textContent="Hello",
                visibility="circles",
                circleIds=[]
            )
        assert "circle_ids is required" in str(exc_info.value).lower()

    def test_circles_post_with_valid_circle_ids(self):
        """Test creating post with valid circle_ids."""
        circle_id = "507f1f77bcf86cd799439011"
        post = PostCreate(
            contentType="note",
            textContent="Hello circle",
            visibility="circles",
            circleIds=[circle_id]
        )
        assert post.visibility == Visibility.circles
        assert post.circle_ids == [circle_id]

    def test_circles_post_with_multiple_circle_ids(self):
        """Test creating post shared to multiple circles."""
        circle_ids = [
            "507f1f77bcf86cd799439011",
            "507f1f77bcf86cd799439022",
            "507f1f77bcf86cd799439033"
        ]
        post = PostCreate(
            contentType="note",
            textContent="Hello circles",
            visibility="circles",
            circleIds=circle_ids
        )
        assert len(post.circle_ids) == 3
        assert post.circle_ids == circle_ids

    def test_invalid_circle_id_format(self):
        """Test that invalid ObjectId format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PostCreate(
                contentType="note",
                textContent="Hello",
                visibility="circles",
                circleIds=["invalid-id"]
            )
        assert "invalid" in str(exc_info.value).lower()

    def test_mixed_valid_invalid_circle_ids(self):
        """Test that one invalid circle_id fails the whole request."""
        with pytest.raises(ValidationError):
            PostCreate(
                contentType="note",
                textContent="Hello",
                visibility="circles",
                circleIds=[
                    "507f1f77bcf86cd799439011",  # Valid
                    "not-valid"  # Invalid
                ]
            )


class TestPostInDBWithVisibility:
    """Tests for PostInDB with visibility fields."""

    def test_post_in_db_with_visibility(self):
        """Test PostInDB includes visibility fields."""
        author = AuthorSchema(userId="123", username="test")
        post = PostInDB(
            contentType="note",
            textContent="Hello",
            author=author,
            visibility="circles",
            circleIds=["507f1f77bcf86cd799439011"]
        )
        assert post.visibility == Visibility.circles
        assert post.circle_ids == ["507f1f77bcf86cd799439011"]

    def test_post_in_db_default_visibility(self):
        """Test PostInDB defaults to public visibility."""
        author = AuthorSchema(userId="123", username="test")
        post = PostInDB(
            contentType="note",
            textContent="Hello",
            author=author
        )
        assert post.visibility == Visibility.public
        assert post.circle_ids is None


class TestPostCreateBackwardsCompatibility:
    """Tests to ensure backwards compatibility with existing posts."""

    def test_existing_post_format_still_works(self):
        """Test that posts without visibility fields still work."""
        # Simulating an old post creation format
        post = PostCreate(
            contentType="note",
            title="My Post",
            textContent="Content here"
        )
        assert post.visibility == Visibility.public
        assert post.circle_ids is None

    def test_all_content_types_work_with_visibility(self):
        """Test all content types work with visibility."""
        content_types = ["note", "link", "image", "document"]

        for ct in content_types:
            # Public post
            post_public = PostCreate(
                contentType=ct,
                textContent="Test",
                visibility="public"
            )
            assert post_public.visibility == Visibility.public

            # Circle post
            post_circle = PostCreate(
                contentType=ct,
                textContent="Test",
                visibility="circles",
                circleIds=["507f1f77bcf86cd799439011"]
            )
            assert post_circle.visibility == Visibility.circles
