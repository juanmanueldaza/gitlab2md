"""Issues parser."""

from collections import Counter
from typing import Any

from ..constants import DEFAULT_TOP_N, MAX_RECENT_ITEMS
from ..registry import register_parser
from .base import BaseParser


@register_parser
class IssuesParser(BaseParser):
    """Parse GitLab issues data."""

    @property
    def section_key(self) -> str:
        return "issues"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        issues = raw_data.get("issues", [])

        states: Counter[str] = Counter()
        projects: Counter[str] = Counter()
        labels: Counter[str] = Counter()
        parsed_issues = []

        for issue in issues:
            state = issue.get("state", "unknown")
            states[state] += 1

            project_path = self._safe_get(issue, "references", "full", default="")
            if project_path:
                # Extract project from reference like "group/project#123"
                project = project_path.rsplit("#", 1)[0]
                projects[project] += 1

            for label in issue.get("labels", []):
                labels[label] += 1

            parsed_issues.append(
                {
                    "title": issue.get("title"),
                    "state": state,
                    "url": issue.get("web_url"),
                    "project": project_path.rsplit("#", 1)[0] if project_path else "",
                    "labels": issue.get("labels", []),
                    "created_at": self._format_date(issue.get("created_at")),
                    "closed_at": self._format_date(issue.get("closed_at")),
                    "confidential": issue.get("confidential", False),
                }
            )

        return {
            "total": len(issues),
            "by_state": dict(states),
            "by_project": dict(projects.most_common(DEFAULT_TOP_N)),
            "top_labels": dict(labels.most_common(DEFAULT_TOP_N)),
            "recent": parsed_issues[:MAX_RECENT_ITEMS],
        }
