"""Snippets formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class SnippetsFormatter(BaseFormatter):
    """Format snippets to Markdown."""

    @property
    def section_key(self) -> str:
        return "snippets"

    @property
    def output_filename(self) -> str:
        return "snippets.md"

    def format(self, data: list[dict[str, Any]]) -> str:
        lines = [f"# Snippets ({len(data)})\n"]

        if not data:
            lines.append("No snippets.")
            return "\n".join(lines)

        for snippet in data:
            title = snippet.get("title", "Untitled")
            url = snippet.get("url", "")
            desc = self._truncate(snippet.get("description"), 100)
            visibility = snippet.get("visibility", "")
            file_name = snippet.get("file_name", "")
            created = snippet.get("created_at", "")

            lines.append(f"## {self._make_link(title, url)}\n")
            if desc:
                lines.append(f"{desc}\n")
            lines.append(f"- **Visibility:** {visibility}")
            if file_name:
                lines.append(f"- **File:** `{file_name}`")
            if created:
                lines.append(f"- **Created:** {created}")
            lines.append("")

        return "\n".join(lines)
