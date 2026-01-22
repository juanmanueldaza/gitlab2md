"""SSH and GPG keys formatter."""

from typing import Any

from ..registry import register_formatter
from .base import BaseFormatter


@register_formatter
class SSHKeysFormatter(BaseFormatter):
    """Format SSH keys to Markdown."""

    @property
    def section_key(self) -> str:
        return "ssh_keys"

    @property
    def output_filename(self) -> str:
        return "ssh_keys.md"

    def format(self, data: list[dict[str, Any]]) -> str:
        lines = [f"# SSH Keys ({len(data)})\n"]

        if not data:
            lines.append("No SSH keys configured.")
            return "\n".join(lines)

        for key in data:
            title = key.get("title", "Untitled")
            created = key.get("created_at", "")
            expires = key.get("expires_at")
            usage = key.get("usage_type", "")

            lines.append(f"## {title}\n")
            if created:
                lines.append(f"- **Created:** {created}")
            if expires:
                lines.append(f"- **Expires:** {expires}")
            if usage:
                lines.append(f"- **Usage:** {usage}")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class GPGKeysFormatter(BaseFormatter):
    """Format GPG keys to Markdown."""

    @property
    def section_key(self) -> str:
        return "gpg_keys"

    @property
    def output_filename(self) -> str:
        return "gpg_keys.md"

    def format(self, data: list[dict[str, Any]]) -> str:
        lines = [f"# GPG Keys ({len(data)})\n"]

        if not data:
            lines.append("No GPG keys configured.")
            return "\n".join(lines)

        for key in data:
            key_id = key.get("key_id", "Unknown")
            created = key.get("created_at", "")

            lines.append(f"## Key: {key_id}\n")
            if created:
                lines.append(f"- **Created:** {created}")
            lines.append("")

        return "\n".join(lines)
