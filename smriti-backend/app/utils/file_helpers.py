"""
File handling utilities.
"""
import os
from pathlib import Path
from typing import Optional, Tuple


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: File name
        
    Returns:
        File extension (without dot)
    """
    return Path(filename).suffix.lstrip('.').lower()


def is_allowed_file_type(filename: str, allowed_extensions: list) -> bool:
    """
    Check if file type is allowed.
    
    Args:
        filename: File name
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if file type is allowed
    """
    ext = get_file_extension(filename)
    return ext in [e.lower() for e in allowed_extensions]


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def validate_file_size(file_size: int, max_size_mb: float = 10.0) -> Tuple[bool, Optional[str]]:
    """
    Validate file size.
    
    Args:
        file_size: File size in bytes
        max_size_mb: Maximum size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    size_mb = file_size / (1024 * 1024)
    
    if size_mb > max_size_mb:
        return False, f"File size exceeds maximum allowed size of {max_size_mb}MB"
    
    return True, None
