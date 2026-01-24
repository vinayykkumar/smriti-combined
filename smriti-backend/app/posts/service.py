import hashlib
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from app.posts.schemas import PostCreate, PostInDB
from app.utils.cloudinary import delete_file
from app.utils.cache import cache
from app.utils.logger import get_logger

logger = get_logger(__name__)

SEARCH_CACHE_PREFIX = "search:"
SEARCH_CACHE_TTL = 300  # 5 minutes

async def get_all_posts(db, skip: int, limit: int):
    cursor = db.posts.find().sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

async def create_post_db(db, post_dict: dict, current_user=None):
    """
    Create a post in the database and trigger notifications.

    Args:
        db: Database connection
        post_dict: Post data to save
        current_user: Current authenticated user (for notifications)

    Returns:
        Created post document
    """
    # 1. Save post to database
    new_post = await db.posts.insert_one(post_dict)
    created_post = await db.posts.find_one({"_id": new_post.inserted_id})

    # 2. Invalidate search cache since new content is available
    _clear_search_cache()

    # 3. Send notifications (fire-and-forget, don't block response)
    if current_user:
        try:
            from app.notifications import service as notification_service
            await notification_service.notify_new_post(db, current_user, created_post)
        except ImportError:
            # Notifications module not available - skip silently
            logger.debug("Notifications module not available")
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Failed to send notification: {e}")
    
    return created_post

async def get_post_by_id(db, post_id: str):
    if not ObjectId.is_valid(post_id):
        return None
    return await db.posts.find_one({"_id": ObjectId(post_id)})

async def delete_post_db(db, post_id: str):
    await db.posts.delete_one({"_id": ObjectId(post_id)})

async def get_posts_by_user(db, user_id: str, skip: int, limit: int):
    cursor = db.posts.find({"author.user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

async def count_posts_by_user(db, user_id: str):
    return await db.posts.count_documents({"author.user_id": user_id})


def _build_search_cache_key(
    q: Optional[str],
    author_id: Optional[str],
    content_type: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    skip: int,
    limit: int
) -> str:
    """Build a deterministic cache key from search parameters."""
    raw = f"{q}|{author_id}|{content_type}|{start_date}|{end_date}|{skip}|{limit}"
    hash_digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{SEARCH_CACHE_PREFIX}{hash_digest}"


def _clear_search_cache():
    """Clear all search-related cache entries."""
    cache.clear()
    logger.debug("Search cache cleared")


async def search_posts(
    db,
    q: Optional[str] = None,
    author_id: Optional[str] = None,
    content_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    """
    Search posts with full-text search and filters.

    Args:
        db: Database connection
        q: Search query text
        author_id: Filter by author's user_id
        content_type: Filter by content type (note, link, image, document)
        start_date: Filter posts created on or after this ISO date
        end_date: Filter posts created on or before this ISO date
        skip: Number of results to skip
        limit: Maximum number of results to return

    Returns:
        dict with 'posts' list and 'total' count
    """
    # Check cache first
    cache_key = _build_search_cache_key(q, author_id, content_type, start_date, end_date, skip, limit)
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.debug(f"Search cache hit for key: {cache_key}")
        return cached_result

    # Build query filter
    query_filter = {}
    sort_criteria = [("created_at", -1)]  # Default sort by newest
    projection = None

    # Full-text search
    if q and q.strip():
        query_filter["$text"] = {"$search": q.strip()}
        # Sort by text relevance score when searching
        sort_criteria = [("score", {"$meta": "textScore"}), ("created_at", -1)]
        projection = {"score": {"$meta": "textScore"}}

    # Author filter
    if author_id:
        query_filter["author.user_id"] = author_id

    # Content type filter
    if content_type:
        query_filter["content_type"] = content_type

    # Date range filters
    if start_date or end_date:
        date_filter = {}
        if start_date:
            try:
                parsed_start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                date_filter["$gte"] = parsed_start.isoformat()
            except (ValueError, AttributeError):
                pass
        if end_date:
            try:
                parsed_end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                date_filter["$lte"] = parsed_end.isoformat()
            except (ValueError, AttributeError):
                pass
        if date_filter:
            query_filter["created_at"] = date_filter

    # Execute count query
    total = await db.posts.count_documents(query_filter)

    # Execute search query
    if projection:
        cursor = db.posts.find(query_filter, projection).sort(sort_criteria).skip(skip).limit(limit)
    else:
        cursor = db.posts.find(query_filter).sort(sort_criteria).skip(skip).limit(limit)

    posts = await cursor.to_list(length=limit)

    result = {
        "posts": posts,
        "total": total
    }

    # Cache the result
    cache.set(cache_key, result, SEARCH_CACHE_TTL)
    logger.debug(f"Search results cached for key: {cache_key}")

    return result
