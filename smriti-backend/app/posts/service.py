import hashlib
from datetime import datetime
from typing import Optional, List, Tuple
from bson import ObjectId
from app.posts.schemas import PostCreate, PostInDB, Visibility
from app.utils.cloudinary import delete_file
from app.utils.cache import cache
from app.utils.logger import get_logger

logger = get_logger(__name__)

SEARCH_CACHE_PREFIX = "search:"
SEARCH_CACHE_TTL = 300  # 5 minutes


# =============================================================================
# CIRCLE POST EXCEPTIONS
# =============================================================================

class PostVisibilityError(Exception):
    """Error related to post visibility/circle permissions."""
    def __init__(self, message: str, code: str = "VISIBILITY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotCircleMemberError(PostVisibilityError):
    """User is not a member of one or more specified circles."""
    def __init__(self, circle_id: str = None):
        message = f"You're not a member of circle {circle_id}" if circle_id else "You're not a member of the specified circle(s)"
        super().__init__(message, "NOT_CIRCLE_MEMBER")
        self.circle_id = circle_id


# =============================================================================
# PUBLIC FEED FUNCTIONS
# =============================================================================

async def get_all_posts(db, skip: int, limit: int):
    """
    Get all PUBLIC posts (excludes circle-only posts).

    This is the main feed - only shows posts with visibility='public'
    or posts without visibility field (backwards compatibility).
    """
    # Only return public posts (or posts without visibility for backwards compat)
    query = {
        "$or": [
            {"visibility": "public"},
            {"visibility": {"$exists": False}}  # Old posts without visibility field
        ]
    }
    cursor = db.posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
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
        visibility = post_dict.get("visibility", "public")
        circle_ids = post_dict.get("circle_ids", [])

        try:
            from app.notifications import service as notification_service

            if visibility == "circles" and circle_ids:
                # Notify circle members
                await notification_service.notify_circle_post(db, current_user, created_post, circle_ids)
            else:
                # Notify all users (public post)
                await notification_service.notify_new_post(db, current_user, created_post)
        except ImportError:
            # Notifications module not available - skip silently
            logger.debug("Notifications module not available")
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Failed to send notification: {e}")

    return created_post


# =============================================================================
# CIRCLE POST FUNCTIONS
# =============================================================================

async def validate_circle_membership_for_post(
    db,
    circle_ids: List[str],
    user_id: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a user is a member of ALL specified circles.

    This MUST be called before creating a post with visibility='circles'.

    Args:
        db: Database connection
        circle_ids: List of circle IDs to validate
        user_id: User ID to check membership for

    Returns:
        Tuple of (is_valid, invalid_circle_id)
        - (True, None) if user is member of all circles
        - (False, circle_id) if user is not a member of that circle
    """
    from app.circles.dependencies import check_membership

    for circle_id in circle_ids:
        is_member = await check_membership(db, circle_id, user_id)
        if not is_member:
            return False, circle_id

    return True, None


async def create_circle_post(
    db,
    post_dict: dict,
    circle_ids: List[str],
    user_id: str,
    current_user=None
) -> dict:
    """
    Create a post in one or more circles.

    This function validates membership BEFORE creating the post.

    Args:
        db: Database connection
        post_dict: Post data to save (without visibility/circle_ids)
        circle_ids: List of circle IDs to post to
        user_id: Author's user ID
        current_user: Current authenticated user (for notifications)

    Returns:
        Created post document

    Raises:
        NotCircleMemberError: If user is not a member of any specified circle
    """
    # Validate membership for ALL circles
    is_valid, invalid_circle_id = await validate_circle_membership_for_post(
        db, circle_ids, user_id
    )

    if not is_valid:
        raise NotCircleMemberError(invalid_circle_id)

    # Add visibility and circle_ids to post
    post_dict["visibility"] = "circles"
    post_dict["circle_ids"] = circle_ids

    # Create the post
    return await create_post_db(db, post_dict, current_user)


async def get_circle_posts(
    db,
    circle_id: str,
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[dict], int]:
    """
    Get posts from a specific circle.

    SECURITY: This function validates membership before returning posts.

    Args:
        db: Database connection
        circle_id: Circle ID to get posts from
        user_id: User ID requesting posts (for membership check)
        skip: Number of posts to skip
        limit: Maximum number of posts to return

    Returns:
        Tuple of (posts list, total count)

    Raises:
        NotCircleMemberError: If user is not a member of the circle
    """
    from app.circles.dependencies import check_membership

    # Validate membership
    is_member = await check_membership(db, circle_id, user_id)
    if not is_member:
        raise NotCircleMemberError(circle_id)

    # Query posts in this circle
    query = {"circle_ids": circle_id}

    total = await db.posts.count_documents(query)
    cursor = db.posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
    posts = await cursor.to_list(length=limit)

    return posts, total


async def get_posts_by_user_with_circles(
    db,
    user_id: str,
    requesting_user_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[dict]:
    """
    Get posts by a specific user, respecting circle privacy.

    - If requesting own posts: Returns ALL posts (public + circles)
    - If requesting other user's posts: Returns only PUBLIC posts

    Args:
        db: Database connection
        user_id: User ID whose posts to fetch
        requesting_user_id: User ID making the request
        skip: Number of posts to skip
        limit: Maximum number of posts to return

    Returns:
        List of post documents
    """
    if user_id == requesting_user_id:
        # User viewing their own posts - show everything
        query = {"author.user_id": user_id}
    else:
        # Viewing someone else's posts - only public
        query = {
            "author.user_id": user_id,
            "$or": [
                {"visibility": "public"},
                {"visibility": {"$exists": False}}
            ]
        }

    cursor = db.posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)


async def enrich_posts_with_circle_names(db, posts: List[dict]) -> List[dict]:
    """
    Add circle names to posts for display purposes.

    Args:
        db: Database connection
        posts: List of post documents

    Returns:
        Posts with circle_names field added
    """
    # Collect all unique circle_ids
    all_circle_ids = set()
    for post in posts:
        circle_ids = post.get("circle_ids", [])
        if circle_ids:
            all_circle_ids.update(circle_ids)

    if not all_circle_ids:
        return posts

    # Fetch circle names
    circle_names_map = {}
    for circle_id in all_circle_ids:
        if ObjectId.is_valid(circle_id):
            circle = await db.circles.find_one(
                {"_id": ObjectId(circle_id)},
                {"name": 1}
            )
            if circle:
                circle_names_map[circle_id] = circle["name"]

    # Enrich posts
    for post in posts:
        circle_ids = post.get("circle_ids", [])
        if circle_ids:
            # Include all circle names, using "Unknown Circle" for deleted circles
            post["circle_names"] = [
                circle_names_map.get(cid, "Unknown Circle")
                for cid in circle_ids
            ]

    return posts

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

    # Build query filter - ONLY search public posts
    query_filter = {
        "$or": [
            {"visibility": "public"},
            {"visibility": {"$exists": False}}  # Backwards compat
        ]
    }
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
