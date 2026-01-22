"""Merge requests parser."""

from collections import Counter
from typing import Any

from ..constants import DEFAULT_TOP_N, MAX_RECENT_ITEMS
from ..registry import register_parser
from .base import BaseParser


@register_parser
class MergeRequestsParser(BaseParser):
    """Parse GitLab merge requests data."""

    @property
    def section_key(self) -> str:
        return "merge_requests"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        mrs = raw_data.get("merge_requests", [])

        states: Counter[str] = Counter()
        projects: Counter[str] = Counter()
        parsed_mrs = []

        for mr in mrs:
            state = mr.get("state", "unknown")
            states[state] += 1

            project_path = self._safe_get(mr, "references", "full", default="")
            if project_path:
                # Extract project from reference like "group/project!123"
                project = project_path.rsplit("!", 1)[0]
                projects[project] += 1

            parsed_mrs.append(
                {
                    "title": mr.get("title"),
                    "state": state,
                    "url": mr.get("web_url"),
                    "project": project_path.rsplit("!", 1)[0] if project_path else "",
                    "created_at": self._format_date(mr.get("created_at")),
                    "merged_at": self._format_date(mr.get("merged_at")),
                }
            )

        return {
            "total": len(mrs),
            "by_state": dict(states),
            "by_project": dict(projects.most_common(DEFAULT_TOP_N)),
            "recent": parsed_mrs[:MAX_RECENT_ITEMS],
        }
