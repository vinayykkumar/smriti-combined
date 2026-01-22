from bson import ObjectId
from app.posts.schemas import PostCreate, PostInDB
from app.utils.cloudinary import delete_file
from app.utils.logger import get_logger

logger = get_logger(__name__)

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
    
    # 2. Send notifications (fire-and-forget, don't block response)
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
