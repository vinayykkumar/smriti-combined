"""
Authentication validation utilities.
"""
from fastapi import HTTPException, status
from app.utils.validators import is_valid_email, is_valid_username, is_valid_password
from app.utils.email_helpers import normalize_email
from typing import Optional


def validate_signup_data(username: str, email: Optional[str], password: str):
    """
    Validate signup data.
    
    Args:
        username: Username to validate
        email: Email to validate (optional)
        password: Password to validate
        
    Raises:
        HTTPException: If validation fails
    """
    if not is_valid_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": "Username must be 3-30 characters (letters, numbers, underscore only)"}
        )
    
    if email and not is_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": "Invalid email format"}
        )
    
    if not is_valid_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": "Password must be at least 6 characters"}
        )


def validate_login_data(identifier: Optional[str], password: str):
    """
    Validate login data.
    
    Args:
        identifier: Username, email, or phone
        password: Password
        
    Raises:
        HTTPException: If validation fails
    """
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": "Username, email, or phone is required"}
        )
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": "Password is required"}
        )


def normalize_user_data(username: str, email: Optional[str] = None):
    """
    Normalize user data (lowercase email, trim username).
    
    Args:
        username: Username
        email: Email (optional)
        
    Returns:
        Tuple of (normalized_username, normalized_email)
    """
    normalized_username = username.strip()
    normalized_email = normalize_email(email) if email else None
    
    return normalized_username, normalized_email
