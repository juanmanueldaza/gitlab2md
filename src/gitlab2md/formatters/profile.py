"""Profile formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class ProfileFormatter(BaseFormatter):
    """Format profile data to Markdown."""

    @property
    def section_key(self) -> str:
        return "profile"

    @property
    def output_filename(self) -> str:
        return "profile.md"

    def format(self, data: dict[str, Any]) -> str:
        lines = [f"# GitLab Profile: {data.get('username', 'Unknown')}\n"]

        if data.get("name"):
            lines.append(f"**{data['name']}**\n")

        if data.get("bio"):
            lines.append(f"> {data['bio']}\n")

        lines.append("## Info\n")

        info_items = [
            ("Job Title", data.get("job_title")),
            ("Organization", data.get("organization")),
            ("Location", data.get("location")),
            ("Website", data.get("website")),
            ("Member since", data.get("created_at")),
        ]

        for label, value in info_items:
            if value:
                lines.append(f"- **{label}:** {value}")

        if data.get("web_url"):
            lines.append(f"\n**Profile:** {data['web_url']}")

        return "\n".join(lines) + "\n"
