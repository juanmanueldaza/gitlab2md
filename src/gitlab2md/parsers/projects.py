"""Projects parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class ProjectsParser(BaseParser):
    """Parse GitLab owned projects data."""

    @property
    def section_key(self) -> str:
        return "projects"

    def parse(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        projects = raw_data.get("projects", [])
        parsed = []

        for project in projects:
            if project.get("forked_from_project"):
                continue  # Skip forks

            parsed.append(self._parse_project(project))

        return sorted(parsed, key=lambda x: (-(x.get("stars") or 0), x.get("name", "")))
