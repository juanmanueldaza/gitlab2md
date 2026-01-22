"""Events parser."""

from collections import Counter
from typing import Any

from ..constants import DEFAULT_TOP_N
from ..registry import register_parser
from .base import BaseParser


@register_parser
class EventsParser(BaseParser):
    """Parse GitLab events (recent activity)."""

    @property
    def section_key(self) -> str:
        return "events"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        events = raw_data.get("events", [])

        action_types: Counter[str] = Counter()
        projects_active: Counter[str] = Counter()

        for event in events:
            action = event.get("action_name", "unknown")
            action_types[action] += 1

            project = self._safe_get(event, "project", "path_with_namespace")
            if project:
                projects_active[project] += 1

        return {
            "total_events": len(events),
            "action_types": dict(action_types.most_common()),
            "active_projects": dict(projects_active.most_common(DEFAULT_TOP_N)),
        }
