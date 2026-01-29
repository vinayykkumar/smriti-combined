"""
Rate limiting for AI Companion endpoints.

Uses in-memory storage for simplicity.
For production with multiple instances, consider Redis-based rate limiting.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Optional
from fastapi import HTTPException, Request

from app.config.settings import settings


class CompanionRateLimiter:
    """
    Simple in-memory rate limiter for companion endpoints.

    Tracks requests per user per endpoint with configurable limits.
    """

    def __init__(self):
        # Structure: {user_id:endpoint: [timestamp1, timestamp2, ...]}
        self._requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        limit: int,
        window_seconds: int = 3600
    ) -> bool:
        """
        Check if request is within rate limit.

        Args:
            user_id: User's ID
            endpoint: Endpoint name (prompt, question, meditation, tts)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds (default 1 hour)

        Returns:
            True if allowed

        Raises:
            HTTPException with 429 status if rate limit exceeded
        """
        async with self._lock:
            key = f"{user_id}:{endpoint}"
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=window_seconds)

            # Clean old requests outside window
            self._requests[key] = [
                ts for ts in self._requests[key]
                if ts > window_start
            ]

            # Check if over limit
            if len(self._requests[key]) >= limit:
                minutes_remaining = window_seconds // 60
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": f"Rate limit exceeded. Maximum {limit} requests per hour for this endpoint.",
                        "retry_after_seconds": window_seconds,
                        "limit": limit,
                        "window_minutes": minutes_remaining
                    }
                )

            # Record this request
            self._requests[key].append(now)
            return True

    def get_remaining(self, user_id: str, endpoint: str, limit: int, window_seconds: int = 3600) -> int:
        """Get remaining requests for a user/endpoint combination."""
        key = f"{user_id}:{endpoint}"
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)

        valid_requests = [
            ts for ts in self._requests.get(key, [])
            if ts > window_start
        ]

        return max(0, limit - len(valid_requests))

    def reset(self, user_id: Optional[str] = None, endpoint: Optional[str] = None):
        """Reset rate limit counters (for testing)."""
        if user_id and endpoint:
            key = f"{user_id}:{endpoint}"
            self._requests.pop(key, None)
        elif user_id:
            keys_to_remove = [k for k in self._requests if k.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                del self._requests[key]
        else:
            self._requests.clear()


# Global rate limiter instance
rate_limiter = CompanionRateLimiter()


# Dependency functions for each endpoint
async def check_prompt_rate_limit(request: Request):
    """Rate limit check for reflection prompt endpoint."""
    user_id = request.state.user.id if hasattr(request.state, 'user') else "anonymous"
    await rate_limiter.check_rate_limit(
        user_id=user_id,
        endpoint="prompt",
        limit=settings.COMPANION_RATE_LIMIT_PROMPT,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )


async def check_question_rate_limit(request: Request):
    """Rate limit check for contemplative question endpoint."""
    user_id = request.state.user.id if hasattr(request.state, 'user') else "anonymous"
    await rate_limiter.check_rate_limit(
        user_id=user_id,
        endpoint="question",
        limit=settings.COMPANION_RATE_LIMIT_QUESTION,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )


async def check_meditation_rate_limit(request: Request):
    """Rate limit check for meditation guidance endpoint."""
    user_id = request.state.user.id if hasattr(request.state, 'user') else "anonymous"
    await rate_limiter.check_rate_limit(
        user_id=user_id,
        endpoint="meditation",
        limit=settings.COMPANION_RATE_LIMIT_MEDITATION,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )


async def check_tts_rate_limit(request: Request):
    """Rate limit check for TTS endpoint."""
    user_id = request.state.user.id if hasattr(request.state, 'user') else "anonymous"
    await rate_limiter.check_rate_limit(
        user_id=user_id,
        endpoint="tts",
        limit=settings.COMPANION_RATE_LIMIT_TTS,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )
