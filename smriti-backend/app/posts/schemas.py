from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

class ContentType(str, Enum):
    note = "note"
    link = "link"
    image = "image"
    document = "document"

class AuthorSchema(BaseModel):
    user_id: str = Field(..., alias="userId")
    username: str

    class Config:
        populate_by_name = True

class PostBase(BaseModel):
    content_type: ContentType = Field(..., alias="contentType")
    title: Optional[str] = Field(None, max_length=200)
    text_content: Optional[str] = Field(None, alias="textContent", max_length=100000) # Max 100KB
    link_url: Optional[str] = Field(None, alias="linkUrl", max_length=2048) # Standard URL limit
    image_url: Optional[str] = Field(None, alias="imageUrl")
    image_public_id: Optional[str] = Field(None, alias="imagePublicId")
    document_url: Optional[str] = Field(None, alias="documentUrl")
    document_type: Optional[str] = Field(None, alias="documentType")
    document_public_id: Optional[str] = Field(None, alias="documentPublicId")

    class Config:
        populate_by_name = True

class PostCreate(PostBase):
    pass

class PostInDB(PostBase):
    author: AuthorSchema
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

class PostResponse(PostInDB):
    post_id: str = Field(alias="_id", serialization_alias="postId")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
