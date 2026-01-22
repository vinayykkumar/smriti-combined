"""
Pagination utilities.
"""
from typing import Optional, Dict, Any, List
from math import ceil


def paginate(
    items: List[Any],
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Dictionary with paginated data and metadata
    """
    # Validate and clamp page_size
    page_size = min(max(1, page_size), max_page_size)
    page = max(1, page)
    
    total_items = len(items)
    total_pages = ceil(total_items / page_size) if total_items > 0 else 0
    
    # Calculate skip
    skip = (page - 1) * page_size
    
    # Get paginated items
    paginated_items = items[skip:skip + page_size]
    
    return {
        "items": paginated_items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


def get_pagination_params(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    default_limit: int = 20,
    max_limit: int = 100
) -> tuple[int, int]:
    """
    Get validated skip and limit parameters.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        page: Page number (alternative to skip)
        page_size: Items per page (alternative to limit)
        default_limit: Default limit if not provided
        max_limit: Maximum allowed limit
        
    Returns:
        Tuple of (skip, limit)
    """
    # Use page/page_size if provided, otherwise use skip/limit
    if page is not None and page_size is not None:
        page = max(1, page)
        page_size = min(max(1, page_size), max_limit)
        skip = (page - 1) * page_size
        limit = page_size
    else:
        skip = max(0, skip or 0)
        limit = min(max(1, limit or default_limit), max_limit)
    
    return skip, limit
