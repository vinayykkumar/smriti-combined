from pydantic import BaseModel, Field
from typing import Literal

class DeviceTokenCreate(BaseModel):
    token: str = Field(..., description="FCM device token")
    platform: Literal["android", "ios"] = Field(..., description="Device platform")

class DeviceTokenResponse(BaseModel):
    success: bool = True
    message: str = "Device token registered successfully"
