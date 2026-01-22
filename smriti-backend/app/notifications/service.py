from app.notifications.repository import NotificationRepository
from app.notifications.schemas import DeviceTokenCreate
from app.auth.schemas import UserResponse
import logging

logger = logging.getLogger(__name__)

async def register_device_token(db, user_id: str, token_data: DeviceTokenCreate):
    """Register a device token for push notifications"""
    repo = NotificationRepository(db)
    await repo.register_token(user_id, token_data.token, token_data.platform)
    logger.info(f"Registered device token for user {user_id}")

async def unregister_device_token(db, token: str):
    """Remove a device token"""
    repo = NotificationRepository(db)
    await repo.remove_token(token)
    logger.info(f"Removed device token")

async def notify_new_post(db, current_user: UserResponse, post: dict):
    """
    Send notification to all users about a new post
    
    Args:
        db: Database connection
        current_user: The author of the post (to exclude them)
        post: The post dictionary that was created
    """
    repo = NotificationRepository(db)
    
    # 1. Get tokens of all other users
    tokens = await repo.get_all_tokens_except_user(str(current_user.id))
    
    if not tokens:
        logger.info("No other devices to notify")
        return

    # 2. Construct message
    post_title = post.get("title")
    
    title = "New Reflection"
    if post_title:
        body = f"{current_user.username} shared: {post_title}"
    else:
        body = f"{current_user.username} shared a new reflection"

    # 3. Send via Firebase
    try:
        from app.utils.firebase import send_push_notification
        result = send_push_notification(
            tokens=tokens,
            title=title,
            body=body,
            data={
                "postId": str(post["_id"]),
                "type": "new_post"
            }
        )
        logger.info(f"Notification result: {result}")
    except ImportError:
        logger.warning("Firebase module not available - skipping push notification")
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
