import time
from fastapi import Request, status, HTTPException

RATE_LIMIT = 30         # requests
WINDOW_SECONDS = 60     # per minute

_requests = {}

def rate_limit(request: Request):
    api_key = request.headers.get("X-API-Key")
    now = time.time()

    timestamps = _requests.get(api_key, [])
    timestamps = [t for t in timestamps if now - t < WINDOW_SECONDS]

    if len(timestamps) >= RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    timestamps.append(now)
    _requests[api_key] = timestamps
