"""Member projects formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class MemberProjectsFormatter(BaseFormatter):
    """Format member projects to Markdown."""

    @property
    def section_key(self) -> str:
        return "member_projects"

    @property
    def output_filename(self) -> str:
        return "member_projects.md"

    def format(self, data: list[dict[str, Any]]) -> str:
        lines = [f"# Member Projects ({len(data)})\n"]
        lines.append("Projects where you are a member but not the owner.\n")

        if not data:
            lines.append("No member projects found.")
            return "\n".join(lines)

        for project in data:
            name = project.get("name", "Unknown")
            url = project.get("url", "")
            desc = (
                self._truncate(self._escape_md(project.get("description")), 100)
                or "No description"
            )
            namespace = project.get("namespace", "")

            lines.append(f"### {self._make_link(name, url)}")
            lines.append(f"**Namespace:** {namespace}\n")
            lines.append(f"{desc}\n")

        return "\n".join(lines)
