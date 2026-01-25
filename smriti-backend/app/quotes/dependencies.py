"""
Dependencies for the Today's Quote feature.

This module provides FastAPI dependencies for authentication and validation.
"""

from fastapi import Header, HTTPException, status
from app.config.settings import get_settings


async def verify_cron_secret(x_cron_secret: str = Header(..., alias="X-Cron-Secret")) -> None:
    """
    Verify the cron secret header for internal endpoints.

    This dependency ensures that only authorized cron jobs can access
    internal endpoints like /api/internal/daily-quote-init and
    /api/internal/daily-quote-push.

    Args:
        x_cron_secret: The X-Cron-Secret header value

    Raises:
        HTTPException 500: If CRON_SECRET is not configured
        HTTPException 401: If the provided secret doesn't match

    Usage:
        @router.post("/internal/endpoint")
        async def internal_endpoint(_: None = Depends(verify_cron_secret)):
            ...
    """
    settings = get_settings()

    # Check if CRON_SECRET is configured
    if not settings.CRON_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "CRON_SECRET not configured. Set it in environment variables."
            }
        )

    # Verify the secret matches
    if x_cron_secret != settings.CRON_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": "Invalid cron secret"
            }
        )


def get_cron_secret_or_none(
    x_cron_secret: str = Header(None, alias="X-Cron-Secret")
) -> str | None:
    """
    Get the cron secret if provided, without validation.

    Useful for endpoints that can be called by both cron jobs and regular users.

    Args:
        x_cron_secret: The X-Cron-Secret header value (optional)

    Returns:
        The secret if provided, None otherwise
    """
    return x_cron_secret


def is_valid_cron_request(x_cron_secret: str | None) -> bool:
    """
    Check if a request has a valid cron secret.

    Helper function for endpoints that accept both cron and user requests.

    Args:
        x_cron_secret: The X-Cron-Secret header value

    Returns:
        True if secret is valid, False otherwise
    """
    if not x_cron_secret:
        return False

    settings = get_settings()
    return settings.CRON_SECRET and x_cron_secret == settings.CRON_SECRET
