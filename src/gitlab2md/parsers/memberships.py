"""Memberships parser."""

from collections import Counter
from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class MembershipsParser(BaseParser):
    """Parse user memberships (groups and projects)."""

    @property
    def section_key(self) -> str:
        return "memberships"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        memberships = raw_data.get("memberships", [])

        source_types: Counter[str] = Counter()
        access_levels: Counter[int] = Counter()
        groups = []
        projects = []

        for membership in memberships:
            source_type = membership.get("source_type", "unknown")
            source_types[source_type] += 1

            access_level = membership.get("access_level", 0)
            access_levels[access_level] += 1

            item = {
                "name": self._safe_get(membership, "source_name"),
                "full_path": self._safe_get(membership, "source_full_path"),
                "access_level": self._get_access_level_name(access_level),
                "created_at": self._format_date(membership.get("created_at")),
            }

            if source_type == "Namespace":
                groups.append(item)
            else:
                projects.append(item)

        return {
            "total": len(memberships),
            "groups": groups,
            "projects": projects,
            "by_access_level": {
                self._get_access_level_name(k): v
                for k, v in access_levels.most_common()
            },
        }
