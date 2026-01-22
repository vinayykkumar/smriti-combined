from app.utils.security import get_password_hash, verify_password, create_access_token
from app.utils.date_helpers import get_current_timestamp
from app.utils.logger import get_logger
from app.auth.schemas import UserCreate, UserResponse
from bson import ObjectId

logger = get_logger(__name__)

async def get_user_by_username(db, username: str):
    return await db.users.find_one({"username": username})

async def get_user_by_email(db, email: str):
    if not email:
        return None
    return await db.users.find_one({"email": email})

async def get_user_by_phone(db, phone: str):
    if not phone:
        return None
    return await db.users.find_one({"phone": phone})

async def create_user(db, user: UserCreate):
    # Check if username exists
    if await get_user_by_username(db, user.username):
        raise ValueError("Username is already taken")
    
    # Validate that at least email or phone is provided
    if not user.email and not user.phone:
        raise ValueError("Either email or phone number is required")
    
    # Check if email exists (if provided)
    if user.email and await get_user_by_email(db, user.email):
        raise ValueError("Email is already registered")
    
    # Check if phone exists (if provided)
    if user.phone and await get_user_by_phone(db, user.phone):
        raise ValueError("Phone number is already registered")
    
    user_dict = user.model_dump()
    # Ensure password is within bcrypt's 72-byte limit
    password = user_dict.pop("password")
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    
    user_dict["hashed_password"] = get_password_hash(password)
    user_dict["created_at"] = get_current_timestamp()
    user_dict["email_verified"] = False
    user_dict["phone_verified"] = False
    
    new_user = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    
    logger.info(
        f"User created: {user.username}",
        extra={"user_id": str(created_user["_id"]), "username": user.username}
    )
    
    return created_user

async def authenticate_user(db, username_or_email: str, password: str):
    # Try to find user by username first
    user = await get_user_by_username(db, username_or_email)
    
    # If not found, try email
    if not user:
        user = await get_user_by_email(db, username_or_email)
    
    if not user:
        logger.warning(f"Authentication failed: user not found", extra={"identifier": username_or_email})
        return None
    if not verify_password(password, user["hashed_password"]):
        logger.warning(f"Authentication failed: invalid password", extra={"username": user.get("username")})
        return None
    
    logger.info(f"User authenticated: {user.get('username')}", extra={"user_id": str(user["_id"])})
    return user

def create_user_token(user_id: str):
    return create_access_token(subject=user_id)
