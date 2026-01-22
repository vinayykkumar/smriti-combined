"""
Text processing utilities.
"""
import re
from typing import Optional


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_hashtags(text: str) -> list[str]:
    """
    Extract hashtags from text.
    
    Args:
        text: Text to extract hashtags from
        
    Returns:
        List of hashtags (without #)
    """
    if not text:
        return []
    
    pattern = r'#(\w+)'
    hashtags = re.findall(pattern, text)
    return list(set(hashtags))  # Remove duplicates


def extract_mentions(text: str) -> list[str]:
    """
    Extract mentions from text.
    
    Args:
        text: Text to extract mentions from
        
    Returns:
        List of mentioned usernames (without @)
    """
    if not text:
        return []
    
    pattern = r'@(\w+)'
    mentions = re.findall(pattern, text)
    return list(set(mentions))  # Remove duplicates


def clean_html(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Text with HTML tags
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Simple HTML tag removal
    clean = re.sub(r'<[^>]+>', '', text)
    return clean.strip()


def word_count(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    if not text:
        return 0
    
    words = text.split()
    return len(words)


def reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes.
    
    Args:
        text: Text to calculate reading time for
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    words = word_count(text)
    minutes = max(1, round(words / words_per_minute))
    return minutes
