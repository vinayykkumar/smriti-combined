from fastapi import APIRouter, Depends, HTTPException, status
from app.database.connection import get_database
from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.notifications.schemas import DeviceTokenCreate, DeviceTokenResponse
from app.notifications import service

router = APIRouter()

@router.post("/register-token", response_model=DeviceTokenResponse)
async def register_token(
    token_data: DeviceTokenCreate,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Register a device token for push notifications.
    Call this after login or when token refreshes.
    """
    await service.register_device_token(db, str(current_user.id), token_data)
    return DeviceTokenResponse()

@router.post("/unregister-token", response_model=DeviceTokenResponse)
async def unregister_token(
    token_data: DeviceTokenCreate,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Remove a device token (call on logout).
    """
    await service.unregister_device_token(db, token_data.token)
    return DeviceTokenResponse(message="Device token removed successfully")
