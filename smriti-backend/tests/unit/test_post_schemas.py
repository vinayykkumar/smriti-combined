"""
Unit tests for post schemas.
"""
import pytest
from app.posts.schemas import PostCreate, ContentType


def test_post_create_schema():
    """Test post creation schema validation."""
    post_data = {
        "contentType": "note",
        "title": "Test Post",
        "textContent": "This is a test"
    }
    post = PostCreate(**post_data)
    assert post.content_type == ContentType.note  # Field name is content_type (alias is contentType)
    assert post.title == "Test Post"


def test_content_type_enum():
    """Test content type enum values."""
    assert ContentType.note == "note"
    assert ContentType.link == "link"
    assert ContentType.document == "document"
