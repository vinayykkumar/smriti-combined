from bson import ObjectId
from app.auth.schemas import UserResponse
from app.posts import service as posts_service


async def get_user_by_id(db, user_id: str) -> dict:
    """
    Get a user by their ObjectId string.

    Args:
        db: Database connection
        user_id: User's ObjectId as string

    Returns:
        dict: User document or None if not found
    """
    if not ObjectId.is_valid(user_id):
        return None
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return user


async def get_user_profile_by_id(db, user_id: str) -> dict:
    """
    Get a public user profile by user_id with statistics.

    Args:
        db: Database connection
        user_id: User's ObjectId as string

    Returns:
        dict: Public profile data with post_count, or None if not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    post_count = await posts_service.count_posts_by_user(db, user_id)

    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "display_name": user.get("display_name"),
        "joined_at": user.get("created_at") or user.get("createdAt"),
        "post_count": post_count
    }


async def get_user_profile_with_stats(db, user: UserResponse) -> dict:
    """
    Get user profile data with statistics
    
    Args:
        db: Database connection
        user: Current authenticated user
        
    Returns:
        dict: User profile data with post_count and other stats
    """
    # Count user's posts
    post_count = await posts_service.count_posts_by_user(db, str(user.id))
    
    # Build profile data
    profile_data = {
        "id": str(user.id),
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "phone": user.phone,
        "joined_at": user.created_at,
        "post_count": post_count
    }
    
    return profile_data
