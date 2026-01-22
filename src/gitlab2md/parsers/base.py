"""Base parser with shared utilities."""

from datetime import datetime
from typing import Any

from ..constants import ACCESS_LEVEL_NAMES


class BaseParser:
    """Base class with utility methods for parsers.

    Provides shared utilities for parsing GitLab API data.
    Single Responsibility: Only provides parsing utilities.
    """

    def _format_date(self, date_str: str | None) -> str | None:
        """Format ISO date to readable format (e.g., 'Jan 2024').

        Args:
            date_str: ISO format date string.

        Returns:
            Formatted date string or original if parsing fails.
        """
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%b %Y")
        except (ValueError, AttributeError):
            return date_str

    def _format_datetime(self, date_str: str | None) -> str | None:
        """Format ISO datetime to readable format (e.g., '2024-01-15 14:30').

        Args:
            date_str: ISO format datetime string.

        Returns:
            Formatted datetime string or original if parsing fails.
        """
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            return date_str

    def _safe_get(self, data: dict[str, Any], *keys: str, default: Any = None) -> Any:
        """Safely get nested dictionary value.

        Args:
            data: The dictionary to traverse.
            *keys: Keys to traverse in order.
            default: Default value if key not found.

        Returns:
            The value at the nested key path, or default.
        """
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
            else:
                return default
        return result

    def _parse_project(self, project: dict[str, Any]) -> dict[str, Any]:
        """Parse common project fields into standardized format.

        DRY helper for consistent project parsing across parsers.

        Args:
            project: Raw project data from GitLab API.

        Returns:
            Standardized project dict with common fields.
        """
        return {
            "name": project.get("name"),
            "path": project.get("path_with_namespace"),
            "description": project.get("description"),
            "visibility": project.get("visibility"),
            "stars": project.get("star_count", 0),
            "forks": project.get("forks_count", 0),
            "url": project.get("web_url"),
            "topics": project.get("topics", []),
            "last_activity": self._format_date(project.get("last_activity_at")),
            "created_at": self._format_date(project.get("created_at")),
        }

    def _get_access_level_name(self, level: int) -> str:
        """Get human-readable name for access level.

        Args:
            level: GitLab access level integer.

        Returns:
            Human-readable access level name.
        """
        return ACCESS_LEVEL_NAMES.get(level, f"Level {level}")
