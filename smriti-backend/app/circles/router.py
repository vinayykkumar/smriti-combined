"""
API Router for Circles (Sangha) feature.

Endpoints:
- POST /circles - Create a new circle
- GET /circles - List user's circles
- GET /circles/{circle_id} - Get circle details
- PATCH /circles/{circle_id} - Update circle
- POST /circles/{circle_id}/regenerate-invite - Regenerate invite code
- GET /circles/preview/{invite_code} - Preview circle before joining
- POST /circles/join - Join a circle via invite code
- GET /circles/{circle_id}/posts - Get circle feed (paginated)
- POST /circles/{circle_id}/posts - Create a post in a circle
- POST /circles/{circle_id}/vote-delete - Vote to delete circle
- DELETE /circles/{circle_id}/vote-delete - Revoke deletion vote
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, UploadFile, File
from typing import Optional, List

from app.database.connection import get_database
from app.auth.schemas import UserResponse
from app.auth.dependencies import get_current_user
from app.utils.response_formatter import success_response
from app.utils.date_helpers import get_current_timestamp
from app.posts.schemas import PostResponse, ContentType

from app.circles.schemas import (
    CircleCreate,
    CircleUpdate,
    CircleJoin,
    CirclePreview,
    CircleDeleteVoteResponse,
)
from app.circles import service
from app.circles.service import (
    CircleNotFoundError,
    CircleFullError,
    AlreadyMemberError,
    InvalidInviteCodeError,
    CircleLimitReachedError,
    CircleServiceError,
    format_circle_response,
    format_circle_list_item,
)
from app.posts.service import (
    get_circle_posts,
    create_circle_post,
    enrich_posts_with_circle_names,
    NotCircleMemberError,
)
from app.posts.validators import validate_post_content
from app.posts.file_upload import process_post_uploads

router = APIRouter()


# =============================================================================
# HELPER: Convert service exceptions to HTTP exceptions
# =============================================================================

def handle_circle_error(e: CircleServiceError) -> HTTPException:
    """Convert service layer errors to HTTP exceptions."""
    status_map = {
        "CIRCLE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CIRCLE_FULL": status.HTTP_409_CONFLICT,
        "ALREADY_MEMBER": status.HTTP_409_CONFLICT,
        "INVALID_INVITE_CODE": status.HTTP_404_NOT_FOUND,
        "CIRCLE_LIMIT_REACHED": status.HTTP_403_FORBIDDEN,
        "NOT_CIRCLE_MEMBER": status.HTTP_403_FORBIDDEN,
        "NO_VOTE": status.HTTP_400_BAD_REQUEST,
    }
    status_code = status_map.get(e.code, status.HTTP_400_BAD_REQUEST)
    return HTTPException(
        status_code=status_code,
        detail={"success": False, "error": e.message, "code": e.code}
    )


# =============================================================================
# CIRCLE CRUD ENDPOINTS
# =============================================================================

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_circle(
    circle_data: CircleCreate,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new circle.

    The creator automatically becomes the first member.
    Maximum 20 circles per user.
    """
    try:
        circle = await service.create_circle(
            db,
            circle_data,
            str(current_user.id),
            current_user.username
        )

        return success_response(
            data={"circle": format_circle_response(circle, str(current_user.id))},
            message="Circle created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)


@router.get("/", response_model=dict)
async def list_circles(
    skip: int = Query(0, ge=0, description="Number of circles to skip"),
    limit: int = Query(20, gt=0, le=50, description="Max circles to return"),
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    List all circles where the current user is a member.

    Returns circles sorted by creation date (newest first).
    Includes last activity timestamp for each circle.
    """
    circles, total = await service.get_user_circles(
        db,
        str(current_user.id),
        skip,
        limit
    )

    return success_response(
        data={
            "circles": [format_circle_list_item(c) for c in circles],
            "total": total,
            "skip": skip,
            "limit": limit
        },
        message="Circles retrieved successfully"
    )


@router.get("/preview/{invite_code}", response_model=dict)
async def preview_circle(
    invite_code: str,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Preview a circle before joining using an invite code.

    Returns limited information (name, color, member count).
    Does not reveal member names or posts.
    """
    try:
        preview = await service.preview_circle(
            db,
            invite_code.strip().upper(),
            str(current_user.id)
        )

        return success_response(
            data={
                "circle": {
                    "name": preview.name,
                    "color": preview.color,
                    "emoji": preview.emoji,
                    "memberCount": preview.member_count,
                    "maxMembers": preview.max_members,
                    "isFull": preview.is_full,
                    "alreadyMember": preview.already_member,
                    "createdAt": preview.created_at.isoformat()
                }
            },
            message="Circle preview retrieved"
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)


@router.get("/{circle_id}", response_model=dict)
async def get_circle_details(
    circle_id: str,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get full details of a circle (members only).

    Returns all circle info including members list and invite code.
    """
    try:
        circle = await service.get_circle(
            db,
            circle_id,
            str(current_user.id)
        )

        return success_response(
            data={"circle": format_circle_response(circle, str(current_user.id))},
            message="Circle retrieved successfully"
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)


@router.patch("/{circle_id}", response_model=dict)
async def update_circle(
    circle_id: str,
    update_data: CircleUpdate,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update circle details (any member can update).

    All members are equal - anyone can change name, description, color, emoji.
    """
    try:
        updated = await service.update_circle(
            db,
            circle_id,
            str(current_user.id),
            update_data
        )

        return success_response(
            data={"circle": format_circle_response(updated, str(current_user.id))},
            message="Circle updated successfully"
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)


# =============================================================================
# JOIN ENDPOINTS
# =============================================================================

@router.post("/join", response_model=dict, status_code=status.HTTP_201_CREATED)
async def join_circle(
    join_data: CircleJoin,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Join a circle using an invite code.

    - Maximum 5 members per circle
    - Maximum 20 circles per user
    - Cannot leave after joining (lifetime commitment)
    """
    try:
        circle = await service.join_circle(
            db,
            join_data.invite_code,
            str(current_user.id),
            current_user.username
        )

        return success_response(
            data={"circle": format_circle_response(circle, str(current_user.id))},
            message="Successfully joined the circle!",
            status_code=status.HTTP_201_CREATED
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)


@router.post("/{circle_id}/regenerate-invite", response_model=dict)
async def regenerate_invite_code(
    circle_id: str,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Regenerate the invite code for a circle (any member can do this).

    The old invite code will stop working immediately.
    """
    try:
        new_code = await service.regenerate_invite_code(
            db,
            circle_id,
            str(current_user.id)
        )

        return success_response(
            data={"inviteCode": new_code},
            message="Invite code regenerated"
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)


# =============================================================================
# CIRCLE FEED ENDPOINTS
# =============================================================================

@router.get("/{circle_id}/posts", response_model=dict)
async def get_circle_feed(
    circle_id: str,
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(20, gt=0, le=100, description="Max posts to return"),
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get posts from a circle (members only).

    Returns posts sorted by creation time (newest first).
    Includes pagination metadata.
    """
    try:
        posts, total = await get_circle_posts(
            db,
            circle_id,
            str(current_user.id),
            skip,
            limit
        )

        # Enrich with circle names for posts shared to multiple circles
        posts = await enrich_posts_with_circle_names(db, posts)

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
            message="Circle posts retrieved successfully"
        )
    except NotCircleMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "error": e.message, "code": e.code}
        )


@router.post("/{circle_id}/posts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_circle_post_endpoint(
    circle_id: str,
    content_type: ContentType = Form(...),
    title: Optional[str] = Form(None),
    text_content: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    document: Optional[UploadFile] = File(None),
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a post in a specific circle (members only).

    The post will only be visible to circle members.
    """
    # Validate post content
    validate_post_content(content_type, text_content, link_url, image, document)

    # Process file uploads
    upload_data = await process_post_uploads(content_type, image, document)

    # Create post document
    post_dict = {
        "content_type": content_type,
        "title": title,
        "text_content": text_content,
        "link_url": link_url,
        **upload_data,
        "author": {
            "user_id": str(current_user.id),
            "username": current_user.username
        },
        "created_at": get_current_timestamp()
    }

    try:
        created_post = await create_circle_post(
            db,
            post_dict,
            [circle_id],
            str(current_user.id),
            current_user
        )

        return success_response(
            data={"post": PostResponse(**{**created_post, "_id": str(created_post["_id"])})},
            message="Post created in circle",
            status_code=status.HTTP_201_CREATED
        )
    except NotCircleMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "error": e.message, "code": e.code}
        )


# =============================================================================
# DELETION VOTE ENDPOINTS
# =============================================================================

@router.post("/{circle_id}/vote-delete", response_model=dict)
async def vote_to_delete_circle(
    circle_id: str,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Vote to delete a circle.

    Circle is deleted only when ALL members have voted.
    This is the only way to "exit" a circle.
    """
    try:
        response, was_deleted = await service.vote_to_delete(
            db,
            circle_id,
            str(current_user.id)
        )

        message = "Circle has been deleted" if was_deleted else "Vote recorded"

        return success_response(
            data={
                "votesNeeded": response.votes_needed,
                "votesCast": response.votes_cast,
                "yourVote": response.your_vote,
                "deleted": response.deleted
            },
            message=message
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)


@router.delete("/{circle_id}/vote-delete", response_model=dict)
async def revoke_deletion_vote(
    circle_id: str,
    db=Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Revoke your vote to delete a circle.

    Can only revoke if you have previously voted.
    """
    try:
        response = await service.revoke_deletion_vote(
            db,
            circle_id,
            str(current_user.id)
        )

        return success_response(
            data={
                "votesNeeded": response.votes_needed,
                "votesCast": response.votes_cast,
                "yourVote": response.your_vote,
                "deleted": False
            },
            message="Vote revoked"
        )
    except CircleServiceError as e:
        raise handle_circle_error(e)
