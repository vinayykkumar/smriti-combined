"""
Pydantic schemas for Circles module.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.circles.constants import (
    MIN_CIRCLE_NAME_LENGTH,
    MAX_CIRCLE_NAME_LENGTH,
    MAX_CIRCLE_DESCRIPTION_LENGTH,
    MAX_MEMBERS_PER_CIRCLE,
    CIRCLE_COLORS,
)


# =============================================================================
# ENUMS
# =============================================================================

class Visibility(str, Enum):
    """Post visibility options."""
    public = "public"
    circles = "circles"


# =============================================================================
# EMBEDDED SCHEMAS
# =============================================================================

class CircleMember(BaseModel):
    """Schema for a member embedded in a circle document."""
    user_id: str = Field(..., alias="userId")
    username: str
    joined_at: datetime = Field(default_factory=datetime.utcnow, alias="joinedAt")

    class Config:
        populate_by_name = True


class CircleCreator(BaseModel):
    """Schema for the circle creator (for historical record, no special powers)."""
    user_id: str = Field(..., alias="userId")
    username: str

    class Config:
        populate_by_name = True


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class CircleCreate(BaseModel):
    """Schema for creating a new circle."""
    name: str = Field(
        ...,
        min_length=MIN_CIRCLE_NAME_LENGTH,
        max_length=MAX_CIRCLE_NAME_LENGTH,
        description="Circle name"
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_CIRCLE_DESCRIPTION_LENGTH,
        description="Optional circle description"
    )
    color: Optional[str] = Field(
        None,
        description="Hex color code from palette"
    )
    emoji: Optional[str] = Field(
        None,
        max_length=10,
        description="Circle emoji"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean circle name."""
        if v:
            v = v.strip()
            if len(v) < MIN_CIRCLE_NAME_LENGTH:
                raise ValueError(f"Name must be at least {MIN_CIRCLE_NAME_LENGTH} characters")
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is from our palette."""
        if v is None:
            return None
        v = v.strip().upper()
        # Normalize to match palette format
        if not v.startswith('#'):
            v = f'#{v}'
        if v.upper() not in [c.upper() for c in CIRCLE_COLORS]:
            raise ValueError(f"Color must be from the allowed palette")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Clean description."""
        if v:
            v = v.strip()
            if len(v) == 0:
                return None
        return v


class CircleJoin(BaseModel):
    """Schema for joining a circle via invite code."""
    invite_code: str = Field(
        ...,
        alias="inviteCode",
        description="8-character invite code"
    )

    @field_validator('invite_code', mode='before')
    @classmethod
    def validate_invite_code(cls, v: str) -> str:
        """Normalize invite code: strip whitespace, uppercase, remove spaces."""
        if isinstance(v, str):
            v = v.strip().upper().replace(" ", "")
            if len(v) != 8:
                raise ValueError("Invite code must be exactly 8 characters")
        return v

    class Config:
        populate_by_name = True


class CircleUpdate(BaseModel):
    """Schema for updating a circle."""
    name: Optional[str] = Field(
        None,
        min_length=MIN_CIRCLE_NAME_LENGTH,
        max_length=MAX_CIRCLE_NAME_LENGTH
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_CIRCLE_DESCRIPTION_LENGTH
    )
    color: Optional[str] = None
    emoji: Optional[str] = Field(None, max_length=10)

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is from our palette."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v.startswith('#'):
            v = f'#{v}'
        if v.upper() not in [c.upper() for c in CIRCLE_COLORS]:
            raise ValueError(f"Color must be from the allowed palette")
        return v

    def has_updates(self) -> bool:
        """Check if any fields have values to update."""
        return any([
            self.name is not None,
            self.description is not None,
            self.color is not None,
            self.emoji is not None,
        ])


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class CircleResponse(BaseModel):
    """Full circle response schema."""
    circle_id: str = Field(..., alias="circleId")
    name: str
    description: Optional[str] = None
    color: str
    emoji: Optional[str] = None
    invite_code: str = Field(..., alias="inviteCode")
    members: List[CircleMember]
    member_count: int = Field(..., alias="memberCount")
    max_members: int = Field(default=MAX_MEMBERS_PER_CIRCLE, alias="maxMembers")
    deletion_votes: int = Field(default=0, alias="deletionVotes")
    my_deletion_vote: bool = Field(default=False, alias="myDeletionVote")
    created_at: datetime = Field(..., alias="createdAt")
    created_by: CircleCreator = Field(..., alias="createdBy")

    class Config:
        populate_by_name = True


class CircleListItem(BaseModel):
    """Circle item for list views (less detail than full response)."""
    circle_id: str = Field(..., alias="circleId")
    name: str
    description: Optional[str] = None
    color: str
    emoji: Optional[str] = None
    member_count: int = Field(..., alias="memberCount")
    max_members: int = Field(default=MAX_MEMBERS_PER_CIRCLE, alias="maxMembers")
    last_activity_at: Optional[datetime] = Field(None, alias="lastActivityAt")

    class Config:
        populate_by_name = True


class CirclePreview(BaseModel):
    """Limited circle info for preview before joining."""
    name: str
    color: str
    emoji: Optional[str] = None
    member_count: int = Field(..., alias="memberCount")
    max_members: int = Field(default=MAX_MEMBERS_PER_CIRCLE, alias="maxMembers")
    is_full: bool = Field(..., alias="isFull")
    already_member: bool = Field(default=False, alias="alreadyMember")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


class CircleDeleteVoteResponse(BaseModel):
    """Response for deletion vote operations."""
    votes_needed: int = Field(..., alias="votesNeeded")
    votes_cast: int = Field(..., alias="votesCast")
    your_vote: bool = Field(..., alias="yourVote")
    deleted: bool = False

    class Config:
        populate_by_name = True


class InviteCodeResponse(BaseModel):
    """Response when regenerating invite code."""
    invite_code: str = Field(..., alias="inviteCode")

    class Config:
        populate_by_name = True


# =============================================================================
# DATABASE DOCUMENT SCHEMA (for internal use)
# =============================================================================

class CircleInDB(BaseModel):
    """Schema representing a circle document in MongoDB."""
    name: str
    description: Optional[str] = None
    color: str
    emoji: Optional[str] = None
    invite_code: str
    members: List[dict]  # List of member dicts
    member_count: int
    max_members: int = MAX_MEMBERS_PER_CIRCLE
    deletion_votes: List[str] = []  # List of user_ids who voted to delete
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: dict  # {user_id, username}

    class Config:
        populate_by_name = True
