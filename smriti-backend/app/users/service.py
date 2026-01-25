from datetime import datetime, timezone
from bson import ObjectId
from app.auth.schemas import UserResponse
from app.posts import service as posts_service
from app.users.schemas import UserUpdate, UserUpdateResponse, LocationData


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

    # Determine if location is required (for Today's Quote feature)
    location_required = user.timezone is None or user.location is None

    # Build profile data
    profile_data = {
        "id": str(user.id),
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "phone": user.phone,
        "timezone": user.timezone,
        "location": user.location.model_dump() if user.location else None,
        "location_required": location_required,
        "joined_at": user.created_at,
        "post_count": post_count
    }

    return profile_data


async def update_user_profile(
    db,
    user_id: str,
    update_data: UserUpdate
) -> UserUpdateResponse:
    """
    Update user profile with timezone and/or location.

    Args:
        db: Database connection
        user_id: User's ObjectId as string
        update_data: Validated update data

    Returns:
        UserUpdateResponse: Updated user profile

    Raises:
        ValueError: If user not found
    """
    # Build update dict from validated data
    db_update = update_data.to_db_update()

    if not db_update:
        # No actual updates, just fetch and return current data
        user = await get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        return _build_update_response(user)

    # Add updated_at timestamp
    db_update["updated_at"] = datetime.now(timezone.utc)

    # Update the user document
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": db_update},
        return_document=True  # Return the updated document
    )

    if not result:
        raise ValueError("User not found")

    return _build_update_response(result)


def _build_update_response(user: dict) -> UserUpdateResponse:
    """Build UserUpdateResponse from user document"""
    location = user.get("location")
    location_data = None

    if location and isinstance(location, dict):
        lat = location.get("latitude")
        lng = location.get("longitude")
        if lat is not None and lng is not None:
            location_data = LocationData(latitude=lat, longitude=lng)

    # Determine if location is required
    location_required = user.get("timezone") is None or location_data is None

    return UserUpdateResponse(
        id=str(user["_id"]),
        username=user.get("username", ""),
        display_name=user.get("display_name"),
        email=user.get("email"),
        phone=user.get("phone"),
        timezone=user.get("timezone"),
        location=location_data,
        location_required=location_required
    )
