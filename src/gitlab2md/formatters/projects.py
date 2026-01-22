"""Projects formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class ProjectsFormatter(BaseFormatter):
    """Format owned projects to Markdown."""

    @property
    def section_key(self) -> str:
        return "projects"

    @property
    def output_filename(self) -> str:
        return "projects.md"

    def format(self, data: list[dict[str, Any]]) -> str:
        lines = [f"# Owned Projects ({len(data)})\n"]

        if not data:
            lines.append("No public projects.")
            return "\n".join(lines)

        for project in data:
            lines.append(self._format_project(project, desc_max_len=150))

        return "\n".join(lines)
