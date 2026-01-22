"""Merge requests formatter."""

from typing import Any

from ..registry import register_formatter
from .base import MR_STATUS_EMOJI, BaseFormatter


@register_formatter
class MergeRequestsFormatter(BaseFormatter):
    """Format merge requests to Markdown."""

    @property
    def section_key(self) -> str:
        return "merge_requests"

    @property
    def output_filename(self) -> str:
        return "merge_requests.md"

    def format(self, data: dict[str, Any]) -> str:
        lines = [f"# Merge Requests ({data.get('total', 0)} total)\n"]

        by_state = data.get("by_state", {})
        if by_state:
            lines.append("## By State\n")
            for state, count in by_state.items():
                lines.append(f"- **{state.title()}:** {count}")

        by_project = data.get("by_project", {})
        if by_project:
            lines.append("\n## By Project\n")
            for project, count in by_project.items():
                lines.append(f"- **{self._escape_md(project)}:** {count} MRs")

        recent = data.get("recent", [])
        if recent:
            lines.append("\n## Recent MRs\n")
            for mr in recent[:15]:
                title = self._truncate(self._escape_md(mr.get("title")), 60)
                url = mr.get("url", "")
                state = mr.get("state", "")
                project = self._escape_md(mr.get("project", ""))

                status_emoji = self._get_status_emoji(state, MR_STATUS_EMOJI)
                lines.append(
                    f"- {status_emoji} {self._make_link(title, url)} ({project})"
                )

        return "\n".join(lines) + "\n"
