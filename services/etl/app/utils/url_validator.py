"""
URL validation for event ingestion.

Ensures only real, accessible URLs are stored in the database.
"""
import httpx
from urllib.parse import urlparse
from typing import Optional


def is_valid_url_format(url: str) -> bool:
    """Check if URL has valid format."""
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def verify_url_exists(url: str, timeout: int = 5) -> bool:
    """
    Verify URL is accessible (HEAD request).
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
    
    Returns:
        True if URL returns 200-399 status, False otherwise
    """
    try:
        response = httpx.head(
            url,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "AGI-Signpost-Tracker/1.0"}
        )
        return 200 <= response.status_code < 400
    except Exception:
        # Try GET as fallback (some servers don't support HEAD)
        try:
            response = httpx.get(
                url,
                timeout=timeout,
                follow_redirects=True,
                headers={"User-Agent": "AGI-Signpost-Tracker/1.0"}
            )
            return 200 <= response.status_code < 400
        except Exception:
            return False


def validate_and_fix_url(url: str, verify_exists: bool = False) -> Optional[str]:
    """
    Validate URL and optionally verify it exists.
    
    Args:
        url: URL to validate
        verify_exists: If True, makes HTTP request to verify URL is accessible
    
    Returns:
        Valid URL or None if invalid
    """
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    if not is_valid_url_format(url):
        return None
    
    if verify_exists:
        if not verify_url_exists(url):
            return None
    
    return url
