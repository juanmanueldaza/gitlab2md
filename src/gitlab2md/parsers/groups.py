"""Groups contributions parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class GroupsParser(BaseParser):
    """Parse GitLab group contributions."""

    @property
    def section_key(self) -> str:
        return "group_contributions"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        contributions = raw_data.get("group_contributions", {})

        parsed = {}
        for group_name, group_data in contributions.items():
            parsed[group_name] = {
                "total_commits": group_data.get("total_commits", 0),
                "projects": group_data.get("projects", []),
            }

        return parsed
