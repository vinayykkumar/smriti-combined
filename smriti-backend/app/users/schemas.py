from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserProfileResponse(BaseModel):
    """User profile with statistics"""
    id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    joined_at: datetime
    post_count: int

    class Config:
        populate_by_name = True
