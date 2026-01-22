from fastapi import APIRouter, Depends
from app.database.connection import get_database
from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.users import service
from app.users.schemas import UserProfileResponse

router = APIRouter()

@router.get("/me", response_model=dict)
async def get_current_user_profile(
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get details of the current user including stats"""
    # Get user profile with statistics
    profile_data = await service.get_user_profile_with_stats(db, current_user)
    
    return {
        "success": True,
        "status": "success",
        "data": {
            "user": profile_data
        }
    }
