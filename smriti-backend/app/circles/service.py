"""
Service layer for Circles - handles business logic.
"""
from typing import Optional, List, Tuple
from datetime import datetime
from bson import ObjectId

from app.circles.repository import CircleRepository
from app.circles.schemas import (
    CircleCreate,
    CircleUpdate,
    CircleResponse,
    CircleListItem,
    CirclePreview,
    CircleMember,
    CircleCreator,
    CircleDeleteVoteResponse,
)
from app.circles.constants import (
    MAX_MEMBERS_PER_CIRCLE,
    MAX_CIRCLES_PER_USER,
    generate_invite_code,
    get_random_color,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CircleServiceError(Exception):
    """Base exception for circle service errors."""
    def __init__(self, message: str, code: str = "CIRCLE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class CircleNotFoundError(CircleServiceError):
    """Circle not found or user is not a member."""
    def __init__(self, message: str = "Circle not found or you're not a member"):
        super().__init__(message, "CIRCLE_NOT_FOUND")


class CircleFullError(CircleServiceError):
    """Circle has reached maximum members."""
    def __init__(self):
        super().__init__(
            f"This circle is full ({MAX_MEMBERS_PER_CIRCLE}/{MAX_MEMBERS_PER_CIRCLE} members)",
            "CIRCLE_FULL"
        )


class AlreadyMemberError(CircleServiceError):
    """User is already a member of the circle."""
    def __init__(self):
        super().__init__("You're already a member of this circle", "ALREADY_MEMBER")


class InvalidInviteCodeError(CircleServiceError):
    """Invalid invite code."""
    def __init__(self):
        super().__init__("Invalid invite code", "INVALID_INVITE_CODE")


class CircleLimitReachedError(CircleServiceError):
    """User has reached maximum number of circles."""
    def __init__(self):
        super().__init__(
            f"You've reached the maximum of {MAX_CIRCLES_PER_USER} circles",
            "CIRCLE_LIMIT_REACHED"
        )


# =============================================================================
# CIRCLE CRUD OPERATIONS
# =============================================================================

async def create_circle(
    db,
    circle_data: CircleCreate,
    user_id: str,
    username: str
) -> dict:
    """
    Create a new circle with the creator as the first member.

    Args:
        db: Database connection
        circle_data: Circle creation data
        user_id: Creator's user ID
        username: Creator's username

    Returns:
        Created circle document

    Raises:
        CircleLimitReachedError: If user has reached max circles
    """
    repo = CircleRepository(db)

    # Check if user has reached circle limit
    circle_count = await repo.count_by_member(user_id)
    if circle_count >= MAX_CIRCLES_PER_USER:
        raise CircleLimitReachedError()

    # Generate unique invite code
    invite_code = generate_invite_code()
    max_attempts = 10
    for _ in range(max_attempts):
        if await repo.is_invite_code_unique(invite_code):
            break
        invite_code = generate_invite_code()

    # Use provided color or generate random
    color = circle_data.color if circle_data.color else get_random_color()

    # Create the first member (creator)
    creator_member = {
        "user_id": user_id,
        "username": username,
        "joined_at": datetime.utcnow()
    }

    # Build circle document
    circle_doc = {
        "name": circle_data.name.strip(),
        "description": circle_data.description.strip() if circle_data.description else None,
        "color": color,
        "emoji": circle_data.emoji,
        "invite_code": invite_code,
        "members": [creator_member],
        "member_count": 1,
        "max_members": MAX_MEMBERS_PER_CIRCLE,
        "deletion_votes": [],
        "created_at": datetime.utcnow(),
        "created_by": {
            "user_id": user_id,
            "username": username
        }
    }

    created_circle = await repo.create(circle_doc)

    logger.info(
        f"Circle created: {created_circle['name']} by {username}",
        extra={"circle_id": str(created_circle["_id"]), "user_id": user_id}
    )

    return created_circle


async def get_circle(
    db,
    circle_id: str,
    user_id: str
) -> dict:
    """
    Get a circle by ID (only if user is a member).

    Args:
        db: Database connection
        circle_id: Circle ID
        user_id: User ID requesting access

    Returns:
        Circle document

    Raises:
        CircleNotFoundError: If circle not found or user not a member
    """
    repo = CircleRepository(db)
    circle = await repo.find_by_id_and_member(circle_id, user_id)

    if not circle:
        raise CircleNotFoundError()

    return circle


async def get_user_circles(
    db,
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[dict], int]:
    """
    Get all circles where user is a member.

    Args:
        db: Database connection
        user_id: User ID
        skip: Number to skip for pagination
        limit: Maximum number to return

    Returns:
        Tuple of (list of circles, total count)
    """
    repo = CircleRepository(db)
    circles = await repo.find_by_member(user_id, skip, limit)
    total = await repo.count_by_member(user_id)

    # Enrich with last activity timestamp
    for circle in circles:
        circle_id = str(circle["_id"])
        last_activity = await repo.get_last_activity(circle_id)
        circle["last_activity_at"] = last_activity

    return circles, total


async def update_circle(
    db,
    circle_id: str,
    user_id: str,
    update_data: CircleUpdate
) -> dict:
    """
    Update a circle (any member can update).

    Args:
        db: Database connection
        circle_id: Circle ID
        user_id: User ID making the update
        update_data: Fields to update

    Returns:
        Updated circle document

    Raises:
        CircleNotFoundError: If circle not found or user not a member
    """
    repo = CircleRepository(db)

    # Verify membership first
    circle = await repo.find_by_id_and_member(circle_id, user_id)
    if not circle:
        raise CircleNotFoundError()

    # Build update dict
    update_dict = {}
    if update_data.name is not None:
        update_dict["name"] = update_data.name.strip()
    if update_data.description is not None:
        update_dict["description"] = update_data.description.strip() if update_data.description else None
    if update_data.color is not None:
        update_dict["color"] = update_data.color
    if update_data.emoji is not None:
        update_dict["emoji"] = update_data.emoji

    if not update_dict:
        return circle  # Nothing to update

    updated = await repo.update(circle_id, update_dict)

    logger.info(
        f"Circle updated: {circle_id}",
        extra={"circle_id": circle_id, "user_id": user_id, "updates": list(update_dict.keys())}
    )

    return updated


# =============================================================================
# JOIN OPERATIONS
# =============================================================================

async def preview_circle(
    db,
    invite_code: str,
    user_id: str
) -> CirclePreview:
    """
    Get limited circle info for preview before joining.

    Args:
        db: Database connection
        invite_code: 8-character invite code
        user_id: User ID requesting preview (to check if already member)

    Returns:
        CirclePreview with limited info

    Raises:
        InvalidInviteCodeError: If code is invalid
    """
    repo = CircleRepository(db)
    circle = await repo.find_by_invite_code(invite_code.upper())

    if not circle:
        raise InvalidInviteCodeError()

    # Check if user is already a member
    already_member = any(
        m["user_id"] == user_id for m in circle.get("members", [])
    )

    return CirclePreview(
        name=circle["name"],
        color=circle["color"],
        emoji=circle.get("emoji"),
        member_count=circle["member_count"],
        max_members=circle.get("max_members", MAX_MEMBERS_PER_CIRCLE),
        is_full=circle["member_count"] >= MAX_MEMBERS_PER_CIRCLE,
        already_member=already_member,
        created_at=circle["created_at"]
    )


async def join_circle(
    db,
    invite_code: str,
    user_id: str,
    username: str
) -> dict:
    """
    Join a circle using an invite code.

    Args:
        db: Database connection
        invite_code: 8-character invite code
        user_id: User ID joining
        username: Username joining

    Returns:
        Circle document after joining

    Raises:
        InvalidInviteCodeError: If code is invalid
        CircleFullError: If circle is full
        AlreadyMemberError: If user is already a member
        CircleLimitReachedError: If user has reached max circles
    """
    repo = CircleRepository(db)

    # Check if user has reached circle limit
    circle_count = await repo.count_by_member(user_id)
    if circle_count >= MAX_CIRCLES_PER_USER:
        raise CircleLimitReachedError()

    # Find circle by invite code
    circle = await repo.find_by_invite_code(invite_code.upper())
    if not circle:
        raise InvalidInviteCodeError()

    circle_id = str(circle["_id"])

    # Check if already a member
    already_member = any(
        m["user_id"] == user_id for m in circle.get("members", [])
    )
    if already_member:
        raise AlreadyMemberError()

    # Check if circle is full
    if circle["member_count"] >= MAX_MEMBERS_PER_CIRCLE:
        raise CircleFullError()

    # Add member (atomic operation handles race conditions)
    updated_circle = await repo.add_member(circle_id, user_id, username)

    if not updated_circle:
        # Atomic operation failed - either full or already member
        # Re-check to give accurate error
        circle = await repo.find_by_id(circle_id)
        if circle["member_count"] >= MAX_MEMBERS_PER_CIRCLE:
            raise CircleFullError()
        raise AlreadyMemberError()

    logger.info(
        f"User joined circle: {circle['name']}",
        extra={"circle_id": circle_id, "user_id": user_id, "username": username}
    )

    return updated_circle


async def regenerate_invite_code(
    db,
    circle_id: str,
    user_id: str
) -> str:
    """
    Regenerate invite code for a circle (any member can do this).

    Args:
        db: Database connection
        circle_id: Circle ID
        user_id: User ID requesting regeneration

    Returns:
        New invite code

    Raises:
        CircleNotFoundError: If circle not found or user not a member
    """
    repo = CircleRepository(db)

    # Verify membership
    circle = await repo.find_by_id_and_member(circle_id, user_id)
    if not circle:
        raise CircleNotFoundError()

    new_code = await repo.regenerate_invite_code(circle_id)

    if not new_code:
        raise CircleServiceError("Failed to generate new invite code")

    logger.info(
        f"Invite code regenerated for circle: {circle_id}",
        extra={"circle_id": circle_id, "user_id": user_id}
    )

    return new_code


# =============================================================================
# DELETION VOTE OPERATIONS
# =============================================================================

async def vote_to_delete(
    db,
    circle_id: str,
    user_id: str
) -> Tuple[CircleDeleteVoteResponse, bool]:
    """
    Cast a vote to delete the circle. If unanimous, circle is deleted.

    Args:
        db: Database connection
        circle_id: Circle ID
        user_id: User ID voting

    Returns:
        Tuple of (vote response, was_deleted)

    Raises:
        CircleNotFoundError: If circle not found or user not a member
    """
    repo = CircleRepository(db)

    # Verify membership and add vote
    updated = await repo.add_deletion_vote(circle_id, user_id)
    if not updated:
        raise CircleNotFoundError()

    member_count = updated["member_count"]
    votes_cast = len(updated.get("deletion_votes", []))
    user_voted = user_id in updated.get("deletion_votes", [])

    # Check if unanimous
    was_deleted = False
    if votes_cast >= member_count:
        # Unanimous! Delete the circle
        logger.info(
            f"Circle deleted by unanimous vote: {updated['name']}",
            extra={"circle_id": circle_id}
        )

        # Orphan posts before deleting
        await repo.orphan_posts_on_delete(circle_id)

        # Delete the circle
        await repo.delete(circle_id)
        was_deleted = True

    response = CircleDeleteVoteResponse(
        votes_needed=member_count,
        votes_cast=votes_cast,
        your_vote=user_voted,
        deleted=was_deleted
    )

    return response, was_deleted


async def revoke_deletion_vote(
    db,
    circle_id: str,
    user_id: str
) -> CircleDeleteVoteResponse:
    """
    Revoke a deletion vote.

    Args:
        db: Database connection
        circle_id: Circle ID
        user_id: User ID revoking vote

    Returns:
        Updated vote response

    Raises:
        CircleNotFoundError: If circle not found or user not a member
        CircleServiceError: If user hasn't voted
    """
    repo = CircleRepository(db)

    # Get current state first
    circle = await repo.find_by_id_and_member(circle_id, user_id)
    if not circle:
        raise CircleNotFoundError()

    # Check if user has voted
    if user_id not in circle.get("deletion_votes", []):
        raise CircleServiceError("You haven't voted to delete this circle", "NO_VOTE")

    # Remove vote
    updated = await repo.remove_deletion_vote(circle_id, user_id)

    member_count = updated["member_count"]
    votes_cast = len(updated.get("deletion_votes", []))
    user_voted = user_id in updated.get("deletion_votes", [])

    return CircleDeleteVoteResponse(
        votes_needed=member_count,
        votes_cast=votes_cast,
        your_vote=user_voted,
        deleted=False
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_circle_response(circle: dict, user_id: str) -> dict:
    """
    Format a circle document for API response.

    Args:
        circle: Raw circle document from DB
        user_id: Current user's ID (to check their deletion vote)

    Returns:
        Formatted circle dict
    """
    deletion_votes = circle.get("deletion_votes", [])

    return {
        "circleId": str(circle["_id"]),
        "name": circle["name"],
        "description": circle.get("description"),
        "color": circle["color"],
        "emoji": circle.get("emoji"),
        "inviteCode": circle["invite_code"],
        "members": [
            {
                "userId": m["user_id"],
                "username": m["username"],
                "joinedAt": m["joined_at"].isoformat() if isinstance(m["joined_at"], datetime) else m["joined_at"]
            }
            for m in circle.get("members", [])
        ],
        "memberCount": circle["member_count"],
        "maxMembers": circle.get("max_members", MAX_MEMBERS_PER_CIRCLE),
        "deletionVotes": len(deletion_votes),
        "myDeletionVote": user_id in deletion_votes,
        "createdAt": circle["created_at"].isoformat() if isinstance(circle["created_at"], datetime) else circle["created_at"],
        "createdBy": {
            "userId": circle["created_by"]["user_id"],
            "username": circle["created_by"]["username"]
        }
    }


def format_circle_list_item(circle: dict) -> dict:
    """
    Format a circle for list view (less detail).

    Args:
        circle: Raw circle document

    Returns:
        Formatted circle dict for list
    """
    last_activity = circle.get("last_activity_at")

    return {
        "circleId": str(circle["_id"]),
        "name": circle["name"],
        "description": circle.get("description"),
        "color": circle["color"],
        "emoji": circle.get("emoji"),
        "memberCount": circle["member_count"],
        "maxMembers": circle.get("max_members", MAX_MEMBERS_PER_CIRCLE),
        "lastActivityAt": last_activity.isoformat() if isinstance(last_activity, datetime) else last_activity
    }
