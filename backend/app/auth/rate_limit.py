import time
from fastapi import Request, status, HTTPException
from app.core.config import settings
from app.observability.logger import JsonLogger

logger = JsonLogger("rate-limit")

_requests = {}

def rate_limit(request: Request):
    """
    Rate limit requests per API key.
    Uses sliding window algorithm in-memory.
    Note: For multi-instance deployments, use Redis-based rate limiting.
    """
    api_key = request.headers.get("X-API-Key", "anonymous")
    now = time.time()
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    limit = settings.RATE_LIMIT_REQUESTS

    # Get or initialize timestamps for this API key
    timestamps = _requests.get(api_key, [])
    
    # Remove timestamps outside the window
    timestamps = [t for t in timestamps if now - t < window]

    # Check if limit exceeded
    if len(timestamps) >= limit:
        logger.log(
            "WARN",
            "rate_limit_exceeded",
            api_key=api_key[:8] + "..." if len(api_key) > 8 else api_key,
            count=len(timestamps),
            limit=limit
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window} seconds."
        )

    # Add current request timestamp
    timestamps.append(now)
    _requests[api_key] = timestamps
    
    # Cleanup old entries periodically
    if len(_requests) > 200:  # Prevent memory leak
        expired_keys = []
        for key, times in _requests.items():
            _requests[key] = [t for t in times if now - t < window]
            if not _requests[key]:
                expired_keys.append(key)

        for key in expired_keys:
            del _requests[key]
