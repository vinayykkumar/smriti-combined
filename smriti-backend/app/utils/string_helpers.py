"""
String manipulation utilities.
"""
import re
from typing import Optional


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        Slug string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def camel_to_snake(text: str) -> str:
    """
    Convert camelCase to snake_case.
    
    Args:
        text: CamelCase string
        
    Returns:
        snake_case string
    """
    if not text:
        return ""
    
    # Insert underscore before uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(text: str) -> str:
    """
    Convert snake_case to camelCase.
    
    Args:
        text: snake_case string
        
    Returns:
        camelCase string
    """
    if not text:
        return ""
    
    components = text.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


def capitalize_words(text: str) -> str:
    """
    Capitalize first letter of each word.
    
    Args:
        text: Text to capitalize
        
    Returns:
        Capitalized text
    """
    if not text:
        return ""
    
    return ' '.join(word.capitalize() for word in text.split())


def remove_whitespace(text: str) -> str:
    """
    Remove all whitespace from string.
    
    Args:
        text: Text to process
        
    Returns:
        Text without whitespace
    """
    if not text:
        return ""
    
    return re.sub(r'\s+', '', text)


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.
    
    Args:
        email: Email address
        
    Returns:
        Masked email (e.g., u***@e***.com)
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    
    # Mask local part
    if len(local) > 2:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    else:
        masked_local = '*' * len(local)
    
    # Mask domain
    domain_parts = domain.split('.')
    if len(domain_parts) >= 2:
        masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 1) + '.' + '.'.join(domain_parts[1:])
    else:
        masked_domain = '*' * len(domain)
    
    return f"{masked_local}@{masked_domain}"
