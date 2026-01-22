"""
Unit tests for security utilities.
"""
import pytest
from app.utils.security import verify_password, get_password_hash


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password produces different hashes."""
    password = "test_password_123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different due to salt
    assert hash1 != hash2
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
