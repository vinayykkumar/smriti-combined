from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.database.connection import get_database
from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.utils.response_formatter import success_response
from app.users import service
from app.users.schemas import UserProfileResponse
from app.posts import service as posts_service
from app.posts.schemas import PostResponse

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_current_user_profile(
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get details of the current user including stats"""
    profile_data = await service.get_user_profile_with_stats(db, current_user)

    return success_response(
        data={"user": profile_data},
        message="Profile retrieved successfully"
    )


@router.get("/{user_id}", response_model=dict)
async def get_user_profile(
    user_id: str,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a user's public profile by user_id"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Invalid user ID format"}
        )

    profile = await service.get_user_profile_by_id(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "User not found"}
        )

    return success_response(
        data={"user": profile},
        message="User profile retrieved successfully"
    )


@router.get("/{user_id}/posts", response_model=dict)
async def get_user_posts(
    user_id: str,
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(20, gt=0, le=100, description="Max posts to return"),
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get posts by a specific user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Invalid user ID format"}
        )

    # Verify user exists
    user = await service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "User not found"}
        )

    posts = await posts_service.get_posts_by_user(db, user_id, skip, limit)
    total = await posts_service.count_posts_by_user(db, user_id)

    return success_response(
        data={
            "posts": [
                PostResponse(**{**post, "_id": str(post["_id"])})
                for post in posts
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        },
        message="User posts retrieved successfully"
    )
