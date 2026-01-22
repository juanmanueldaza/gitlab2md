"""Groups formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class GroupsFormatter(BaseFormatter):
    """Format group contributions to Markdown."""

    @property
    def section_key(self) -> str:
        return "group_contributions"

    @property
    def output_filename(self) -> str:
        return "groups.md"

    def format(self, data: dict[str, Any]) -> str:
        lines = ["# Group Contributions\n"]

        if not data:
            lines.append("No group contributions tracked.")
            return "\n".join(lines)

        for group_name, group_data in data.items():
            total = group_data.get("total_commits", 0)
            projects = group_data.get("projects", [])

            lines.append(f"## {group_name}\n")
            lines.append(f"**Total commits:** {total}\n")

            if projects:
                lines.append("### Projects contributed to:\n")
                for proj in projects:
                    name = proj.get("name", "Unknown")
                    commits = proj.get("commits", 0)
                    url = proj.get("url", "")
                    lines.append(f"- {self._make_link(name, url)}: {commits} commits")

            lines.append("")

        return "\n".join(lines)
