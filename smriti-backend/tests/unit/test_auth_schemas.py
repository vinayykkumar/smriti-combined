"""
Unit tests for authentication schemas.
"""
import pytest
from app.auth.schemas import UserCreate, LoginRequest


def test_user_create_schema():
    """Test user create schema validation."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    user = UserCreate(**user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_login_request_schema():
    """Test login request schema validation."""
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    login = LoginRequest(**login_data)
    assert login.username == "testuser"
