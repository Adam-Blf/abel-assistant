"""
===============================================================================
PII_REDACTOR.PY - Personal Information Redaction
===============================================================================
A.B.E.L. Project - Secure Logging Support
Redacts sensitive data before logging
===============================================================================
"""

import re
from typing import Any, Dict, Set

# =============================================================================
# REDACTION PATTERNS
# =============================================================================

PII_PATTERNS: Dict[str, tuple[str, str]] = {
    "email": (
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[EMAIL_REDACTED]",
    ),
    "phone": (
        r"(\+?1?\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}",
        "[PHONE_REDACTED]",
    ),
    "jwt_token": (
        r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
        "[JWT_REDACTED]",
    ),
    "api_key_google": (
        r"AIza[0-9A-Za-z\-_]{35}",
        "[GOOGLE_API_KEY_REDACTED]",
    ),
    "api_key_generic": (
        r"(api[_-]?key|apikey|key)[\"']?\s*[:=]\s*[\"']?[\w-]{20,}",
        "[API_KEY_REDACTED]",
    ),
    "password_field": (
        r"(password|passwd|pwd)[\"']?\s*[:=]\s*[\"']?[^\s\"']+",
        "[PASSWORD_REDACTED]",
    ),
    "credit_card": (
        r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
        "[CC_REDACTED]",
    ),
    "ssn": (
        r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        "[SSN_REDACTED]",
    ),
    "bearer_token": (
        r"Bearer\s+[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
        "Bearer [TOKEN_REDACTED]",
    ),
}

# Keys that should be fully redacted when found in dictionaries
SENSITIVE_KEYS: Set[str] = {
    "password",
    "passwd",
    "pwd",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "secret_key",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "credit_card",
    "card_number",
    "cvv",
    "ssn",
    "social_security",
}


def redact_pii(text: str) -> str:
    """
    Redact all PII from text.

    Args:
        text: Input text potentially containing PII

    Returns:
        Text with all PII redacted
    """
    if not isinstance(text, str):
        return str(text)

    result = text
    for _pattern_name, (pattern, replacement) in PII_PATTERNS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def redact_dict(
    data: Dict[str, Any],
    sensitive_keys: Set[str] | None = None,
    max_depth: int = 10,
) -> Dict[str, Any]:
    """
    Redact PII from dictionary values recursively.

    Args:
        data: Dictionary to redact
        sensitive_keys: Set of keys to fully redact (uses default if None)
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        Dictionary with PII redacted
    """
    if max_depth <= 0:
        return {"_truncated": "max depth reached"}

    keys_to_check = sensitive_keys or SENSITIVE_KEYS
    result: Dict[str, Any] = {}

    for key, value in data.items():
        key_lower = key.lower()

        # Fully redact sensitive keys
        if key_lower in keys_to_check:
            result[key] = "[REDACTED]"
        elif isinstance(value, str):
            result[key] = redact_pii(value)
        elif isinstance(value, dict):
            result[key] = redact_dict(value, keys_to_check, max_depth - 1)
        elif isinstance(value, list):
            result[key] = [
                redact_dict(item, keys_to_check, max_depth - 1)
                if isinstance(item, dict)
                else redact_pii(str(item))
                if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            result[key] = value

    return result


def safe_log_data(data: Any) -> Any:
    """
    Prepare data for safe logging by redacting PII.

    Args:
        data: Any data to be logged

    Returns:
        Data safe for logging
    """
    if isinstance(data, dict):
        return redact_dict(data)
    elif isinstance(data, str):
        return redact_pii(data)
    elif isinstance(data, list):
        return [safe_log_data(item) for item in data]
    else:
        return data
