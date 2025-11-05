"""
Authentication and authorization for admin endpoints.

SECURITY: All admin routes must use these dependencies.
"""

from secrets import compare_digest
from fastapi import Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# Rate limiter for admin endpoints
limiter = Limiter(key_func=get_remote_address)


def verify_api_key(x_api_key: str = Header(...)) -> str:
    """
    Verify admin API key using constant-time comparison.
    
    SECURITY:
    - Uses secrets.compare_digest() to prevent timing attacks
    - Returns consistent error message (no key length leakage)
    - Should be combined with rate limiting on routes
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        The validated API key (for logging/audit purposes)
        
    Raises:
        HTTPException(403): If key is missing or invalid
    """
    # Constant-time comparison prevents timing attacks
    if not compare_digest(x_api_key, settings.admin_api_key):
        # TODO: Add audit logging here
        # log_failed_auth(request, x_api_key[:8] + "...")
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return x_api_key


def verify_api_key_optional(x_api_key: str = Header(None)) -> str | None:
    """
    Optional API key verification for endpoints that support both public and admin access.
    
    Returns None if no key provided, validated key if provided and valid.
    Raises 403 if key provided but invalid.
    """
    if x_api_key is None:
        return None
    
    if not compare_digest(x_api_key, settings.admin_api_key):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return x_api_key

