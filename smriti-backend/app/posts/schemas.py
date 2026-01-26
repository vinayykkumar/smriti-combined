from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId


class ContentType(str, Enum):
    """Type of content in a post."""
    note = "note"
    link = "link"
    image = "image"
    document = "document"


class Visibility(str, Enum):
    """Post visibility options."""
    public = "public"      # Visible to everyone in the main feed
    circles = "circles"    # Visible only to members of specified circles
    private = "private"    # Visible only to the author (used when circle is deleted)

class AuthorSchema(BaseModel):
    user_id: str = Field(..., alias="userId")
    username: str

    class Config:
        populate_by_name = True

class PostBase(BaseModel):
    content_type: ContentType = Field(..., alias="contentType")
    title: Optional[str] = Field(None, max_length=200)
    text_content: Optional[str] = Field(None, alias="textContent", max_length=100000)  # Max 100KB
    link_url: Optional[str] = Field(None, alias="linkUrl", max_length=2048)  # Standard URL limit
    image_url: Optional[str] = Field(None, alias="imageUrl")
    image_public_id: Optional[str] = Field(None, alias="imagePublicId")
    document_url: Optional[str] = Field(None, alias="documentUrl")
    document_type: Optional[str] = Field(None, alias="documentType")
    document_public_id: Optional[str] = Field(None, alias="documentPublicId")

    class Config:
        populate_by_name = True


class PostCreate(PostBase):
    """Schema for creating a new post with visibility options."""
    visibility: Visibility = Field(
        default=Visibility.public,
        description="Post visibility: 'public' for everyone, 'circles' for specific circles only"
    )
    circle_ids: Optional[List[str]] = Field(
        None,
        alias="circleIds",
        description="List of circle IDs to share the post with (required if visibility is 'circles')"
    )

    @model_validator(mode='after')
    def validate_visibility_and_circles(self) -> 'PostCreate':
        """
        Validate that circle_ids is provided when visibility is 'circles',
        and empty/null when visibility is 'public'.
        """
        if self.visibility == Visibility.circles:
            if not self.circle_ids or len(self.circle_ids) == 0:
                raise ValueError("circle_ids is required when visibility is 'circles'")
            # Validate ObjectId format
            for cid in self.circle_ids:
                if not ObjectId.is_valid(cid):
                    raise ValueError(f"Invalid circle_id format: {cid}")
        elif self.visibility == Visibility.public:
            if self.circle_ids and len(self.circle_ids) > 0:
                raise ValueError("circle_ids must be empty when visibility is 'public'")
        return self

    class Config:
        populate_by_name = True

class PostInDB(PostBase):
    """Schema for a post document in the database."""
    author: AuthorSchema
    visibility: Visibility = Field(default=Visibility.public)
    circle_ids: Optional[List[str]] = Field(None, alias="circleIds")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True


class PostResponse(PostInDB):
    """Schema for post API responses."""
    post_id: str = Field(alias="_id", serialization_alias="postId")
    # Optional: include circle names for display convenience
    circle_names: Optional[List[str]] = Field(None, alias="circleNames")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
