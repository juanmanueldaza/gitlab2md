"""Base formatter with shared utilities."""

import urllib.parse
from typing import Any

from ..constants import (
    ALLOWED_URL_SCHEMES,
    DEFAULT_TRUNCATE_LENGTH,
    ISSUE_STATUS_EMOJI,
    MAX_TOPICS_DISPLAY,
    MR_STATUS_EMOJI,
)

# Re-export for backward compatibility
__all__ = ["BaseFormatter", "MR_STATUS_EMOJI", "ISSUE_STATUS_EMOJI"]


class BaseFormatter:
    """Base class with utility methods for formatters.

    Provides shared utilities for Markdown formatting with security.
    Single Responsibility: Only provides formatting utilities.
    """

    def _escape_md(self, text: str | None) -> str:
        """Escape markdown special characters in user-provided text.

        Escapes characters that could break markdown table rendering
        or cause unintended formatting, based on GFM spec.
        """
        if not text:
            return ""
        # Must escape backslash first to prevent double-escaping
        text = text.replace("\\", "\\\\")
        text = text.replace("`", "\\`")
        text = text.replace("*", "\\*")
        text = text.replace("_", "\\_")
        text = text.replace("{", "\\{")
        text = text.replace("}", "\\}")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace("(", "\\(")
        text = text.replace(")", "\\)")
        text = text.replace("#", "\\#")
        text = text.replace("+", "\\+")
        text = text.replace("-", "\\-")
        text = text.replace(".", "\\.")
        text = text.replace("!", "\\!")
        text = text.replace("<", "\\<")
        text = text.replace(">", "\\>")
        text = text.replace("~", "\\~")
        # Escape pipe for tables and newlines for inline text
        return text.replace("|", "\\|").replace("\n", " ").replace("\r", "")

    def _escape_pipe(self, text: str | None) -> str:
        """Escape pipe characters for Markdown tables."""
        if not text:
            return ""
        return text.replace("|", "\\|")

    def _sanitize_url(self, url: str | None) -> str:
        """Sanitize URL for safe inclusion in Markdown.

        - Only allows http, https, mailto schemes
        - Escapes characters that could break Markdown link syntax
        - Returns empty string for invalid/dangerous URLs

        Args:
            url: The URL to sanitize.

        Returns:
            Sanitized URL safe for Markdown, or empty string if invalid.
        """
        if not url:
            return ""

        url = url.strip()
        if not url:
            return ""

        # Parse and validate scheme
        try:
            parsed = urllib.parse.urlparse(url)
            # Require non-empty scheme to prevent protocol-relative URLs
            if not parsed.scheme or parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
                return ""
        except Exception:
            return ""

        # Escape characters that break Markdown link syntax
        # ) breaks [text](url) syntax
        # [ and ] can interfere with nested links
        url = url.replace(")", "%29")
        url = url.replace("[", "%5B")
        url = url.replace("]", "%5D")

        return url

    def _make_link(self, text: str, url: str | None) -> str:
        """Create a markdown link with sanitized URL.

        Args:
            text: The link text.
            url: The URL (will be sanitized).

        Returns:
            Markdown link if URL is valid, otherwise just the text.
        """
        if not url:
            return text
        safe_url = self._sanitize_url(url)
        if not safe_url:
            return text
        return f"[{text}]({safe_url})"

    def _truncate(
        self, text: str | None, max_len: int = DEFAULT_TRUNCATE_LENGTH
    ) -> str:
        """Truncate text to max length.

        Args:
            text: The text to truncate.
            max_len: Maximum length (default from constants).

        Returns:
            Truncated text with ellipsis if needed.
        """
        if not text:
            return ""
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."

    def _format_project(
        self, project: dict[str, Any], desc_max_len: int = DEFAULT_TRUNCATE_LENGTH
    ) -> str:
        """Format a project item as Markdown.

        Shared helper for consistent project formatting across formatters.

        Args:
            project: Project data dict with name, url, description, etc.
            desc_max_len: Max length for description truncation.

        Returns:
            Formatted Markdown string for the project.
        """
        name = project.get("name", "Unknown")
        url = project.get("url", "")
        desc = self._truncate(self._escape_md(project.get("description")), desc_max_len)
        desc = desc or "No description"
        visibility = project.get("visibility", "unknown")
        stars = project.get("stars", 0)
        forks = project.get("forks", 0)
        topics = project.get("topics", [])
        last_activity = project.get("last_activity", "")

        lines = []
        lines.append(f"### {self._make_link(name, url)}\n")
        lines.append(f"{desc}\n")
        lines.append(
            f"- **Visibility:** {visibility} | **Stars:** {stars} | **Forks:** {forks}"
        )

        if topics:
            topic_str = ", ".join(topics[:MAX_TOPICS_DISPLAY])
            if len(topics) > MAX_TOPICS_DISPLAY:
                topic_str += f" (+{len(topics) - MAX_TOPICS_DISPLAY} more)"
            lines.append(f"- **Topics:** {topic_str}")

        if last_activity:
            lines.append(f"- **Last activity:** {last_activity}")

        lines.append("")
        return "\n".join(lines)

    def _get_status_emoji(self, state: str, emoji_map: dict[str, str]) -> str:
        """Get status emoji for a state.

        Args:
            state: The state string (e.g., 'opened', 'closed').
            emoji_map: Mapping of states to emojis.

        Returns:
            Emoji string or '?' if state unknown.
        """
        return emoji_map.get(state, "?")
