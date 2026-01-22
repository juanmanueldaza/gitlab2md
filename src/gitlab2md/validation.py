"""Shared validation utilities for gitlab2md.

Centralizes input validation logic to avoid duplication (DRY principle).
Used by both CLI and extractor modules.
"""

import re

from .constants import MAX_NAME_LENGTH

# GitLab username/group name validation pattern
# - Must start and end with alphanumeric character
# - Can contain alphanumeric, underscore, hyphen, or dot in the middle
# - No consecutive special characters
_VALID_NAME_PATTERN = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9_.\-]*[a-zA-Z0-9])?$|^[a-zA-Z0-9]$"
)


def validate_gitlab_name(name: str, field: str = "name") -> None:
    """Validate a GitLab username or group name.

    GitLab naming rules:
    - Must start and end with alphanumeric character
    - Can contain alphanumeric characters, underscores, hyphens, and dots
    - No consecutive special characters
    - Maximum 255 characters

    Args:
        name: The name to validate.
        field: Field name for error messages (e.g., 'username', 'group').

    Raises:
        ValueError: If name is invalid with descriptive message.
    """
    if not name or not name.strip():
        raise ValueError(f"{field} cannot be empty")

    name = name.strip()

    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"{field} too long (max {MAX_NAME_LENGTH} characters)")

    # Check for consecutive special characters
    if ".." in name or "--" in name or "__" in name or ".-" in name or "-." in name:
        raise ValueError(
            f"Invalid {field} format: '{name}'. "
            "Cannot contain consecutive special characters."
        )

    if not _VALID_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid {field} format: '{name}'. "
            "Must start and end with alphanumeric character. "
            "Only alphanumeric characters, underscores, hyphens, and dots are allowed."
        )


def validate_filename(filename: str) -> None:
    """Validate a filename for safe file operations.

    Args:
        filename: The filename to validate.

    Raises:
        ValueError: If filename contains dangerous characters or patterns.
    """
    if "\x00" in filename:
        raise ValueError("Invalid filename: contains null byte")

    if ".." in filename:
        raise ValueError(f"Invalid filename: {filename}")

    if filename.startswith("/"):
        raise ValueError(f"Invalid filename: {filename}")

    if filename.startswith("\\") or (len(filename) > 1 and filename[1] == ":"):
        raise ValueError(f"Invalid filename: {filename}")
