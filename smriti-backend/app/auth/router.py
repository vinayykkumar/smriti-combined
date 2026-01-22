from fastapi import APIRouter, Depends, HTTPException, status
from app.database.connection import get_database
from app.auth.schemas import UserCreate, UserResponse, LoginRequest, AuthResponse
from app.auth.dependencies import get_current_user
from app.utils.response_formatter import success_response, error_response
from app.utils.logger import log_error
from app.auth import service

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=dict)
async def signup(user: UserCreate, db = Depends(get_database)):
    try:
        created_user = await service.create_user(db, user)
        
        # Convert ObjectId to string for Pydantic
        user_id = str(created_user["_id"])
        
        # Create token
        access_token = service.create_user_token(user_id)
        
        return success_response(
            data={
                "username": created_user["username"],
                "displayName": created_user.get("display_name"),
                "email": created_user.get("email"),
                "phone": created_user.get("phone"),
                "token": access_token
            },
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as e:
        # Username already taken
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "error": str(e)}
        )
    except Exception as e:
        # Log the actual error for debugging
        log_error(e, context="User signup")
        raise

@router.post("/login", response_model=dict)
async def login(login_data: LoginRequest, db = Depends(get_database)):
    # Validate that at least one identifier is provided
    if not login_data.username and not login_data.email and not login_data.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": "Username, email, or phone is required"}
        )
    
    # Use whichever is provided (priority: username > email > phone)
    identifier = login_data.username or login_data.email or login_data.phone
    
    # Authenticate user
    user = await service.authenticate_user(db, identifier, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": "Incorrect credentials"}
        )
        
    # Convert ObjectId to string
    user_id = str(user["_id"])
    
    # Create token
    access_token = service.create_user_token(user_id)
    
    return success_response(
        data={
            "username": user["username"],
            "displayName": user.get("display_name"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "token": access_token
        },
        message="Login successful"
    )

@router.get("/check-username/{username}", response_model=dict)
async def check_username(username: str, db = Depends(get_database)):
    """Check if username is available"""
    existing_user = await db.users.find_one({"username": username})
    
    return {
        "success": True,
        "available": existing_user is None,
        "message": "Username is available" if existing_user is None else "Username is already taken"
    }

@router.get("/me", response_model=dict)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return {
        "success": True,
        "user": current_user
    }
