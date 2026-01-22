from app.auth.schemas import UserResponse
from app.posts import service as posts_service

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
