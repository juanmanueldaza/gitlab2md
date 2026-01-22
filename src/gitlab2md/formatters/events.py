"""Events formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class EventsFormatter(BaseFormatter):
    """Format events to Markdown."""

    @property
    def section_key(self) -> str:
        return "events"

    @property
    def output_filename(self) -> str:
        return "activity.md"

    def format(self, data: dict[str, Any]) -> str:
        lines = ["# Recent Activity\n"]
        lines.append(f"Total events: {data.get('total_events', 0)}\n")

        action_types = data.get("action_types", {})
        if action_types:
            lines.append("## Activity Types\n")
            for action, count in action_types.items():
                lines.append(f"- **{self._escape_md(action)}:** {count}")

        active_projects = data.get("active_projects", {})
        if active_projects:
            lines.append("\n## Most Active Projects\n")
            for project, count in active_projects.items():
                # Properly escape project name and sanitize URL
                escaped_project = self._escape_md(project)
                url = self._sanitize_url(f"https://gitlab.com/{project}")
                if url:
                    lines.append(
                        f"- {self._make_link(escaped_project, url)}: {count} events"
                    )
                else:
                    lines.append(f"- {escaped_project}: {count} events")

        return "\n".join(lines) + "\n"
