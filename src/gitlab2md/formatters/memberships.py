"""Memberships formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class MembershipsFormatter(BaseFormatter):
    """Format memberships to Markdown."""

    @property
    def section_key(self) -> str:
        return "memberships"

    @property
    def output_filename(self) -> str:
        return "memberships.md"

    def format(self, data: dict[str, Any]) -> str:
        total = data.get("total", 0)
        lines = [f"# Memberships ({total} total)\n"]

        by_access = data.get("by_access_level", {})
        if by_access:
            lines.append("## By Access Level\n")
            for level, count in by_access.items():
                lines.append(f"- **{level}:** {count}")

        groups = data.get("groups", [])
        if groups:
            lines.append(f"\n## Groups ({len(groups)})\n")
            for group in groups:
                name = group.get("name", "Unknown")
                path = group.get("full_path", "")
                access = group.get("access_level", "")
                lines.append(f"- **{name}** (`{path}`) - {access}")

        projects = data.get("projects", [])
        if projects:
            lines.append(f"\n## Projects ({len(projects)})\n")
            for project in projects:
                name = project.get("name", "Unknown")
                path = project.get("full_path", "")
                access = project.get("access_level", "")
                lines.append(f"- **{name}** (`{path}`) - {access}")

        if not groups and not projects:
            lines.append("No memberships found.")

        return "\n".join(lines) + "\n"
