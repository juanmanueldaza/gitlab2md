"""Member projects parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class MemberProjectsParser(BaseParser):
    """Parse projects where user is a member."""

    @property
    def section_key(self) -> str:
        return "member_projects"

    def parse(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        projects = raw_data.get("member_projects", [])
        username = raw_data.get("username", "")
        parsed = []

        for project in projects:
            # Skip if user owns this project
            namespace = project.get("namespace", {})
            if namespace.get("path") == username:
                continue

            project_data = self._parse_project(project)
            project_data["namespace"] = namespace.get("name")
            parsed.append(project_data)

        return parsed
