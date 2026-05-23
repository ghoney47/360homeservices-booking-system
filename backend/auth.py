"""Simple API-key guard for admin/internal routes."""
import os
from fastapi import Header, HTTPException, status

_API_KEY = os.getenv("ADMIN_API_KEY")


async def require_api_key(x_api_key: str = Header(...)):
    if not _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_API_KEY is not configured on this server",
        )
    if x_api_key != _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
