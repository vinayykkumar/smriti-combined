"""
Email validation and formatting utilities.
"""
import re
from typing import Optional


def normalize_email(email: str) -> Optional[str]:
    """
    Normalize email address (lowercase, trim).
    
    Args:
        email: Email address to normalize
        
    Returns:
        Normalized email or None if invalid
    """
    if not email:
        return None
    
    email = email.strip().lower()
    
    if not is_valid_email(email):
        return None
    
    return email


def is_valid_email(email: str) -> bool:
    """
    Validate email format (more comprehensive).
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid email format
    """
    if not email:
        return False
    
    # RFC 5322 compliant regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def extract_domain(email: str) -> Optional[str]:
    """
    Extract domain from email address.
    
    Args:
        email: Email address
        
    Returns:
        Domain name or None
    """
    if not email or '@' not in email:
        return None
    
    return email.split('@')[1].lower()
