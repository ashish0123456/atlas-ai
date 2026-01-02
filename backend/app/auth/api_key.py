import os
from fastapi import Request, status, HTTPException

VALID_API_KEYS = set(
    key.strip()
    for key in os.getenv("API_KEYS", "").split(",")
    if key.strip()
)

def validate_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")

    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )