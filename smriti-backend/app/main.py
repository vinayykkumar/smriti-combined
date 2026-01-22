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
from app.middleware.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)
from fastapi.exceptions import RequestValidationError

@app.exception_handler(HTTPException)
async def http_exception_handler_wrapper(request, exc: HTTPException):
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler_wrapper(request, exc: RequestValidationError):
    return await validation_exception_handler(request, exc)

@app.exception_handler(Exception)
async def global_exception_handler_wrapper(request, exc: Exception):
    return await global_exception_handler(request, exc)

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
