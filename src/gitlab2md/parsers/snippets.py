"""Snippets parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class SnippetsParser(BaseParser):
    """Parse user snippets data."""

    @property
    def section_key(self) -> str:
        return "snippets"

    def parse(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        snippets = raw_data.get("snippets", [])
        parsed = []

        for snippet in snippets:
            parsed.append(
                {
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "visibility": snippet.get("visibility"),
                    "url": snippet.get("web_url"),
                    "file_name": snippet.get("file_name"),
                    "created_at": self._format_date(snippet.get("created_at")),
                    "updated_at": self._format_date(snippet.get("updated_at")),
                }
            )

        return parsed
