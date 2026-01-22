from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Unique handle like @johndoe")
    display_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Display name (not unique)")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
    email: Optional[str] = Field(None, min_length=5, max_length=100, description="Email for verification")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Phone for verification")
    
    @field_validator('email', 'phone')
    def validate_contact(cls, v, info):
        # At least one of email or phone must be provided
        return v

class UserInDB(UserBase):
    hashed_password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    email_verified: bool = False
    phone_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")

    class Config:
        populate_by_name = True

class LoginRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    password: str = Field(..., min_length=6, max_length=128)

class UserResponse(UserBase):
    id: Optional[str] = Field(alias="_id", default=None)
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class AuthResponse(BaseModel):
    """Response model for auth endpoints matching API design"""
    user_id: str = Field(alias="userId")
    username: str
    
    class Config:
        populate_by_name = True
