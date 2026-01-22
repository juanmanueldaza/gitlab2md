"""Starred projects parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class StarredProjectsParser(BaseParser):
    """Parse starred projects data."""

    @property
    def section_key(self) -> str:
        return "starred_projects"

    def parse(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        projects = raw_data.get("starred_projects", [])
        parsed = [self._parse_project(project) for project in projects]

        return sorted(parsed, key=lambda x: (-(x.get("stars") or 0), x.get("name", "")))
