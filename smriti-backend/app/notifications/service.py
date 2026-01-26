from typing import List
from app.notifications.repository import NotificationRepository
from app.notifications.schemas import DeviceTokenCreate
from app.auth.schemas import UserResponse
import logging

logger = logging.getLogger(__name__)


async def get_circle_member_ids(db, circle_ids: List[str]) -> List[str]:
    """
    Get all unique member user IDs from the specified circles.

    Args:
        db: Database connection
        circle_ids: List of circle IDs

    Returns:
        List of unique user IDs
    """
    from bson import ObjectId

    member_ids = set()
    for circle_id in circle_ids:
        if ObjectId.is_valid(circle_id):
            circle = await db.circles.find_one(
                {"_id": ObjectId(circle_id)},
                {"members.user_id": 1}
            )
            if circle:
                for member in circle.get("members", []):
                    member_ids.add(member["user_id"])

    return list(member_ids)

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


async def notify_circle_post(db, current_user: UserResponse, post: dict, circle_ids: List[str]):
    """
    Send notification to circle members about a new post.

    Only notifies members of the specified circles, excluding the author.

    Args:
        db: Database connection
        current_user: The author of the post (to exclude them)
        post: The post dictionary that was created
        circle_ids: List of circle IDs the post was shared to
    """
    repo = NotificationRepository(db)

    # 1. Get member IDs from all circles
    member_ids = await get_circle_member_ids(db, circle_ids)

    if not member_ids:
        logger.info("No circle members to notify")
        return

    # 2. Get tokens for those members (excluding author)
    tokens = await repo.get_tokens_for_users(member_ids, exclude_user_id=str(current_user.id))

    if not tokens:
        logger.info("No device tokens found for circle members")
        return

    # 3. Get circle names for the notification
    circle_names = []
    from bson import ObjectId
    for circle_id in circle_ids:
        if ObjectId.is_valid(circle_id):
            circle = await db.circles.find_one(
                {"_id": ObjectId(circle_id)},
                {"name": 1}
            )
            if circle:
                circle_names.append(circle["name"])

    # 4. Construct message
    post_title = post.get("title")
    circle_name = circle_names[0] if circle_names else "a circle"

    if len(circle_names) > 1:
        title = f"New in {len(circle_names)} circles"
    else:
        title = f"New in {circle_name}"

    if post_title:
        body = f"{current_user.username} shared: {post_title}"
    else:
        body = f"{current_user.username} shared a new reflection"

    # 5. Send via Firebase
    try:
        from app.utils.firebase import send_push_notification
        result = send_push_notification(
            tokens=tokens,
            title=title,
            body=body,
            data={
                "postId": str(post["_id"]),
                "type": "circle_post",
                "circleIds": ",".join(circle_ids)
            }
        )
        logger.info(f"Circle notification result: {result}")
    except ImportError:
        logger.warning("Firebase module not available - skipping push notification")
    except Exception as e:
        logger.error(f"Failed to send circle push notification: {e}")
