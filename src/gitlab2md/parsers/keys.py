"""SSH and GPG keys parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class SSHKeysParser(BaseParser):
    """Parse SSH keys data."""

    @property
    def section_key(self) -> str:
        return "ssh_keys"

    def parse(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        keys = raw_data.get("ssh_keys", [])
        parsed = []

        for key in keys:
            parsed.append(
                {
                    "title": key.get("title"),
                    "created_at": self._format_date(key.get("created_at")),
                    "expires_at": self._format_date(key.get("expires_at")),
                    "usage_type": key.get("usage_type"),
                }
            )

        return parsed


@register_parser
class GPGKeysParser(BaseParser):
    """Parse GPG keys data."""

    @property
    def section_key(self) -> str:
        return "gpg_keys"

    def parse(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        keys = raw_data.get("gpg_keys", [])
        parsed = []

        for key in keys:
            parsed.append(
                {
                    "created_at": self._format_date(key.get("created_at")),
                    "key_id": key.get("key_id"),
                }
            )

        return parsed
