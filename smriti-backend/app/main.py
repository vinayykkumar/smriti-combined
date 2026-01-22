from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.logging_config import setup_logging
from app.database.connection import db
from app.auth.router import router as auth_router
from app.posts.router import router as posts_router
from app.users.router import router as users_router
from app.notifications.router import router as notifications_router
from app.middleware.cors import setup_cors
from app.utils.logger import get_logger
import logging

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS (Cross-Origin Resource Sharing) - using utility function
setup_cors(app)

# Request logging middleware
from app.middleware.logging import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)

# Exception Handlers
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom handler for HTTPException to return API design format"""
    from app.utils.response_formatter import error_response
    
    # If detail is already a dict with our format, use it
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    # Otherwise use error_response formatter
    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Convert validation errors (422) to 400 with custom message"""
    errors = exc.errors()
    
    # Extract field name and create custom message
    if errors:
        first_error = errors[0]
        field = first_error.get("loc", [])[-1] if first_error.get("loc") else "field"
        error_type = first_error.get("type", "")
        error_msg_raw = first_error.get("msg", "")
        
        # Custom messages for common validation errors
        # Check for string length validation (Pydantic v2 uses "string_too_short")
        if field == "password" and ("min_length" in error_type or "string_too_short" in error_type or "at least 6" in error_msg_raw):
            error_msg = "Password must be at least 6 characters long"
        elif field == "username" and ("min_length" in error_type or "string_too_short" in error_type or "at least 3" in error_msg_raw):
            error_msg = "Username must be at least 3 characters long"
        elif field == "password" and "missing" in error_type:
            error_msg = "Password is required"
        elif field == "username" and "missing" in error_type:
            error_msg = "Username is required"
        else:
            # Use default message for other validation errors
            error_msg = error_msg_raw if error_msg_raw else "Invalid input"
    else:
        error_msg = "Invalid input"
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": error_msg
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    from app.utils.response_formatter import error_response
    from app.utils.logger import log_error
    
    # Log the error
    log_error(exc, context=f"Unhandled exception in {request.url.path}")
    
    return error_response(
        message="Something went wrong on the server. Please try again.",
        status_code=500
    )

# Database events
@app.on_event("startup")
async def startup_db_client():
    db.connect()
    # Initialize Firebase after logging is set up
    from app.utils.firebase import init_firebase
    init_firebase()

@app.on_event("shutdown")
async def shutdown_db_client():
    db.close()

# Routes
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(posts_router, prefix=f"{settings.API_V1_STR}/posts", tags=["Posts"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(notifications_router, prefix=f"{settings.API_V1_STR}/notifications", tags=["Notifications"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Smriti API 🌳",
        "docs": "/docs",
        "version": settings.VERSION
    }

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def api_health():
    """Simple health check endpoint"""
    return {"status": "ok"}
