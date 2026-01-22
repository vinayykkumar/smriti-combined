"""
Unit tests for authentication schemas.
"""
import pytest
from app.auth.schemas import UserSignup, UserLogin


def test_user_signup_schema():
    """Test user signup schema validation."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    user = UserSignup(**user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_user_login_schema():
    """Test user login schema validation."""
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    login = UserLogin(**login_data)
    assert login.username == "testuser"
