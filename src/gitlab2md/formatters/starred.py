"""Starred projects formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class StarredProjectsFormatter(BaseFormatter):
    """Format starred projects to Markdown."""

    @property
    def section_key(self) -> str:
        return "starred_projects"

    @property
    def output_filename(self) -> str:
        return "starred.md"

    def format(self, data: list[dict[str, Any]]) -> str:
        lines = [f"# Starred Projects ({len(data)})\n"]

        if not data:
            lines.append("No starred projects.")
            return "\n".join(lines)

        for project in data:
            lines.append(self._format_project(project, desc_max_len=150))

        return "\n".join(lines)
