"""
CORS middleware configuration.
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.config.settings import settings


def setup_cors(app: FastAPI):
    """
    Setup CORS middleware.
    
    Args:
        app: FastAPI application instance
    """
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:19006",  # Expo default
        "exp://localhost:19000",   # Expo
    ]
    
    # Add production origins if configured
    if hasattr(settings, 'ALLOWED_ORIGINS'):
        allowed_origins.extend(settings.ALLOWED_ORIGINS)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
