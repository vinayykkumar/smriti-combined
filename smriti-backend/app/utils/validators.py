"""
Validation utilities for Smriti Backend.
"""
import re
from typing import Optional


def is_valid_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username: Username string to validate
        
    Returns:
        True if username is valid, False otherwise
    """
    if not username:
        return False
    
    # Username: 3-30 chars, alphanumeric and underscore only
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return bool(re.match(pattern, username))


def is_valid_password(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password: Password string to validate
        
    Returns:
        True if password meets requirements, False otherwise
    """
    if not password:
        return False
    
    # Minimum 6 characters
    if len(password) < 6:
        return False
    
    return True


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input.
    
    Args:
        value: String to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Strip whitespace
    sanitized = value.strip()
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
