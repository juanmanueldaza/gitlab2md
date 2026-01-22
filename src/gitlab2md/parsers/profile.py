"""Profile parser."""

from typing import Any

from ..registry import register_parser
from .base import BaseParser


@register_parser
class ProfileParser(BaseParser):
    """Parse GitLab user profile data."""

    @property
    def section_key(self) -> str:
        return "profile"

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        profile_list = raw_data.get("profile", [])
        profile = profile_list[0] if profile_list else {}

        return {
            "username": profile.get("username") or raw_data.get("username"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "location": profile.get("location"),
            "website": profile.get("website_url"),
            "organization": profile.get("organization"),
            "job_title": profile.get("job_title"),
            "state": profile.get("state"),
            "created_at": self._format_date(profile.get("created_at")),
            "avatar_url": profile.get("avatar_url"),
            "web_url": profile.get("web_url"),
        }
