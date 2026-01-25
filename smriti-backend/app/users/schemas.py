from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class LocationData(BaseModel):
    """User location coordinates"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class UserProfileResponse(BaseModel):
    """User profile with statistics"""
    id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    location: Optional[LocationData] = None
    location_required: bool = False
    joined_at: datetime
    post_count: int

    class Config:
        populate_by_name = True


class UserUpdate(BaseModel):
    """Schema for updating user profile (PATCH /api/users/me)"""
    timezone: Optional[str] = Field(
        None,
        description="IANA timezone string (e.g., 'America/New_York', 'Asia/Kolkata')"
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Latitude coordinate (-90 to 90)"
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Longitude coordinate (-180 to 180)"
    )

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        """Validate that timezone is a valid IANA timezone string"""
        if v is None:
            return None

        # Try to instantiate the timezone to verify it's valid
        # This works on all platforms (Windows, Linux, macOS)
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(
                f"Invalid timezone: '{v}'. Must be a valid IANA timezone "
                f"(e.g., 'America/New_York', 'Europe/London', 'Asia/Kolkata')"
            )

        return v

    @model_validator(mode='after')
    def validate_location_pair(self) -> 'UserUpdate':
        """Ensure latitude and longitude are both provided together or both None"""
        lat = self.latitude
        lng = self.longitude

        # Both None is fine
        if lat is None and lng is None:
            return self

        # Both provided is fine
        if lat is not None and lng is not None:
            return self

        # One provided without the other is an error
        raise ValueError(
            "Both latitude and longitude must be provided together. "
            "You cannot update only one coordinate."
        )

    def has_updates(self) -> bool:
        """Check if any fields have values to update"""
        return any([
            self.timezone is not None,
            self.latitude is not None,
            self.longitude is not None
        ])

    def to_db_update(self) -> dict:
        """Convert to database update dict, only including non-None fields"""
        update = {}

        if self.timezone is not None:
            update["timezone"] = self.timezone

        if self.latitude is not None and self.longitude is not None:
            update["location"] = {
                "latitude": self.latitude,
                "longitude": self.longitude
            }

        return update


class UserUpdateResponse(BaseModel):
    """Response after updating user profile"""
    id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    location: Optional[LocationData] = None
    location_required: bool = Field(
        default=False,
        description="True if user should be prompted to set location"
    )

    class Config:
        populate_by_name = True
