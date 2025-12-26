"""
A.B.E.L - Helper Utilities
"""

import uuid
import re
from datetime import datetime
from typing import Optional

import pytz


def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    return sanitized or "unnamed"


def format_datetime(
    dt: datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    timezone: str = "Europe/Paris",
) -> str:
    """
    Format a datetime object to string.

    Args:
        dt: Datetime object
        format_str: Format string
        timezone: Timezone name

    Returns:
        Formatted datetime string
    """
    tz = pytz.timezone(timezone)
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    local_dt = dt.astimezone(tz)
    return local_dt.strftime(format_str)


def parse_datetime(
    date_str: str,
    format_str: Optional[str] = None,
) -> Optional[datetime]:
    """
    Parse a datetime string.

    Args:
        date_str: Date string to parse
        format_str: Optional format string

    Returns:
        Datetime object or None if parsing fails
    """
    formats = [
        format_str,
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
    ]

    for fmt in formats:
        if fmt:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

    return None


def is_valid_email(email: str) -> bool:
    """Check if an email address is valid."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    pattern = r"^https?://[^\s<>\"{}|\\^`\[\]]+"
    return bool(re.match(pattern, url))


def extract_urls(text: str) -> list:
    """Extract all URLs from text."""
    pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
    return re.findall(pattern, text)


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data, showing only first/last characters.

    Args:
        value: String to mask
        visible_chars: Number of visible characters on each end

    Returns:
        Masked string
    """
    if len(value) <= visible_chars * 2:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars * 2) + value[-visible_chars:]
