"""Contributed projects formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class ContributedProjectsFormatter(BaseFormatter):
    """Format contributed projects to Markdown."""

    @property
    def section_key(self) -> str:
        return "contributed_projects"

    @property
    def output_filename(self) -> str:
        return "contributions.md"

    def format(self, data: list[dict[str, Any]]) -> str:
        lines = [f"# Contributed Projects ({len(data)})\n"]

        if not data:
            lines.append("No contributed projects found.")
            return "\n".join(lines)

        lines.append("Projects you have contributed to (excluding your own):\n")

        for project in data:
            lines.append(self._format_project(project, desc_max_len=150))

        return "\n".join(lines)
