"""
URL validation for event ingestion.

Ensures only real, accessible URLs are stored in the database.
Detects and flags synthetic/fixture URLs to prevent hallucination.
"""
import re
from urllib.parse import urlparse

import httpx

# Known synthetic/fixture domains and patterns
SYNTHETIC_DOMAINS = {
    'dev-fixture.local',
    'localhost',
    'example.com',
    'example.org',
    'test.local',
    'fixture.test',
}

# URL patterns that indicate synthetic/fixture data
SYNTHETIC_PATTERNS = [
    r'/[a-f0-9]{8,}$',  # Hash-only paths like /a3f2c1d8e9
    r'/synthetic/',
    r'/fixture/',
    r'/test/',
    r'/fake/',
    r'/mock/',
    r'/tech/\d+$',  # Suspicious numeric-only paths like /tech/60
]


def is_synthetic_url(url: str) -> bool:
    """
    Detect if URL is synthetic/fixture data.

    Checks against known test domains and suspicious patterns.

    Args:
        url: URL to check

    Returns:
        True if URL appears to be synthetic/fixture
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # Check against known synthetic domains
        if domain in SYNTHETIC_DOMAINS:
            return True

        # Check for wildcard matches (*.test, *.local)
        if domain.endswith('.test') or domain.endswith('.local'):
            return True

        # Check against synthetic path patterns
        for pattern in SYNTHETIC_PATTERNS:
            if re.search(pattern, path):
                return True

        # Check for obviously fake hash-based URLs
        # E.g., https://openai.com/blog/a3f2c1d8e9
        if re.match(r'^/[^/]+/[a-f0-9]{8,}$', path):
            return True

        return False

    except Exception:
        return False


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


def validate_and_fix_url(
    url: str,
    verify_exists: bool = False,
    allow_synthetic: bool = False
) -> tuple[str | None, bool]:
    """
    Validate URL and optionally verify it exists.

    Args:
        url: URL to validate
        verify_exists: If True, makes HTTP request to verify URL is accessible
        allow_synthetic: If True, allows synthetic/fixture URLs (for testing)

    Returns:
        Tuple of (valid_url or None, is_synthetic)
    """
    if not url or not isinstance(url, str):
        return None, False

    url = url.strip()

    if not is_valid_url_format(url):
        return None, False

    # Check if URL is synthetic
    synthetic = is_synthetic_url(url)

    # Reject synthetic URLs unless explicitly allowed
    if synthetic and not allow_synthetic:
        return None, True

    # Verify URL exists if requested (skip for synthetic URLs)
    if verify_exists and not synthetic:
        if not verify_url_exists(url):
            return None, False

    return url, synthetic
