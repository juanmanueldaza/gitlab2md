"""Issues formatter."""

from typing import Any

from ..registry import register_formatter
from .base import ISSUE_STATUS_EMOJI, BaseFormatter


@register_formatter
class IssuesFormatter(BaseFormatter):
    """Format issues to Markdown."""

    @property
    def section_key(self) -> str:
        return "issues"

    @property
    def output_filename(self) -> str:
        return "issues.md"

    def format(self, data: dict[str, Any]) -> str:
        lines = [f"# Issues ({data.get('total', 0)} total)\n"]

        by_state = data.get("by_state", {})
        if by_state:
            lines.append("## By State\n")
            for state, count in by_state.items():
                lines.append(f"- **{state.title()}:** {count}")

        by_project = data.get("by_project", {})
        if by_project:
            lines.append("\n## By Project\n")
            for project, count in by_project.items():
                lines.append(f"- **{self._escape_md(project)}:** {count} issues")

        top_labels = data.get("top_labels", {})
        if top_labels:
            lines.append("\n## Top Labels\n")
            for label, count in top_labels.items():
                lines.append(f"- `{self._escape_md(label)}`: {count}")

        recent = data.get("recent", [])
        if recent:
            lines.append("\n## Recent Issues\n")
            for issue in recent[:15]:
                title = self._truncate(self._escape_md(issue.get("title")), 60)
                url = issue.get("url", "")
                state = issue.get("state", "")
                project = self._escape_md(issue.get("project", ""))

                status_emoji = self._get_status_emoji(state, ISSUE_STATUS_EMOJI)
                conf = " [confidential]" if issue.get("confidential") else ""
                link = self._make_link(title, url)
                lines.append(f"- {status_emoji} {link}{conf} ({project})")

        return "\n".join(lines) + "\n"
