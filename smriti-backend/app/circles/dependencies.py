"""
FastAPI dependencies for Circles module.
Provides reusable security checks for circle membership verification.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from bson import ObjectId

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.database.connection import get_database
from app.circles.repository import CircleRepository
from app.circles.constants import MAX_MEMBERS_PER_CIRCLE


class CircleMembershipError(HTTPException):
    """Exception raised when user is not a member of a circle."""
    def __init__(self, detail: str = "Circle not found or you're not a member"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class CircleNotFoundError(HTTPException):
    """Exception raised when circle doesn't exist."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Circle not found"
        )


async def check_membership(
    db,
    circle_id: str,
    user_id: str
) -> bool:
    """
    Check if a user is a member of a circle.

    This is the core security check used throughout the circles module.

    Args:
        db: Database connection
        circle_id: Circle ID to check
        user_id: User ID to verify

    Returns:
        True if user is a member, False otherwise
    """
    if not ObjectId.is_valid(circle_id):
        return False

    repo = CircleRepository(db)
    return await repo.is_member(circle_id, user_id)


async def check_membership_for_circles(
    db,
    circle_ids: list[str],
    user_id: str
) -> tuple[bool, Optional[str]]:
    """
    Check if a user is a member of ALL specified circles.

    Used when creating a post that targets multiple circles.

    Args:
        db: Database connection
        circle_ids: List of circle IDs to check
        user_id: User ID to verify

    Returns:
        Tuple of (all_valid, first_invalid_circle_id)
        - (True, None) if user is member of all circles
        - (False, circle_id) if user is not a member of that circle
    """
    repo = CircleRepository(db)

    for circle_id in circle_ids:
        if not ObjectId.is_valid(circle_id):
            return False, circle_id

        is_member = await repo.is_member(circle_id, user_id)
        if not is_member:
            return False, circle_id

    return True, None


async def get_circle_if_member(
    db,
    circle_id: str,
    user_id: str
) -> dict:
    """
    Get a circle document only if the user is a member.

    This combines the membership check with fetching the circle data,
    which is more efficient than separate calls.

    Args:
        db: Database connection
        circle_id: Circle ID
        user_id: User ID to verify

    Returns:
        Circle document

    Raises:
        CircleMembershipError: If user is not a member or circle doesn't exist
    """
    if not ObjectId.is_valid(circle_id):
        raise CircleMembershipError()

    repo = CircleRepository(db)
    circle = await repo.find_by_id_and_member(circle_id, user_id)

    if not circle:
        raise CircleMembershipError()

    return circle


async def verify_circle_membership(
    circle_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
) -> dict:
    """
    FastAPI dependency that verifies user is a member of a circle.

    Use this as a dependency in route handlers that require circle membership.
    Returns the circle document if authorized.

    Usage:
        @router.get("/{circle_id}/posts")
        async def get_posts(
            circle: dict = Depends(verify_circle_membership),
            ...
        ):
            # circle is guaranteed to exist and user is a member
            pass

    Args:
        circle_id: Circle ID from path parameter
        current_user: Current authenticated user (from auth dependency)
        db: Database connection

    Returns:
        Circle document

    Raises:
        HTTPException 403: If circle not found or user is not a member
    """
    return await get_circle_if_member(db, circle_id, str(current_user.id))


async def verify_can_join_circle(
    db,
    circle_id: str,
    user_id: str
) -> tuple[dict, str]:
    """
    Verify that a user can join a circle.

    Checks:
    1. Circle exists
    2. Circle is not full
    3. User is not already a member

    Args:
        db: Database connection
        circle_id: Circle ID
        user_id: User ID wanting to join

    Returns:
        Tuple of (circle_document, None) if can join

    Raises:
        Various errors based on why joining failed
    """
    repo = CircleRepository(db)
    circle = await repo.find_by_id(circle_id)

    if not circle:
        return None, "CIRCLE_NOT_FOUND"

    # Check if full
    if circle["member_count"] >= MAX_MEMBERS_PER_CIRCLE:
        return None, "CIRCLE_FULL"

    # Check if already member
    is_member = any(m["user_id"] == user_id for m in circle.get("members", []))
    if is_member:
        return None, "ALREADY_MEMBER"

    return circle, None


def get_member_from_circle(circle: dict, user_id: str) -> Optional[dict]:
    """
    Get a specific member's data from a circle document.

    Args:
        circle: Circle document
        user_id: User ID to find

    Returns:
        Member dict or None if not found
    """
    for member in circle.get("members", []):
        if member["user_id"] == user_id:
            return member
    return None


def is_circle_creator(circle: dict, user_id: str) -> bool:
    """
    Check if a user is the original creator of a circle.

    Note: In our design, creators have NO special powers.
    This is purely for informational purposes (e.g., showing "Creator" badge).

    Args:
        circle: Circle document
        user_id: User ID to check

    Returns:
        True if user is the creator, False otherwise
    """
    created_by = circle.get("created_by", {})
    return created_by.get("user_id") == user_id
