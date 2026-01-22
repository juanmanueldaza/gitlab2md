"""Tests for all parsers."""

import pytest

from gitlab2md.parsers.base import BaseParser
from gitlab2md.parsers.contributed import ContributedProjectsParser
from gitlab2md.parsers.events import EventsParser
from gitlab2md.parsers.groups import GroupsParser
from gitlab2md.parsers.issues import IssuesParser
from gitlab2md.parsers.keys import GPGKeysParser, SSHKeysParser
from gitlab2md.parsers.member_projects import MemberProjectsParser
from gitlab2md.parsers.memberships import MembershipsParser
from gitlab2md.parsers.merge_requests import MergeRequestsParser
from gitlab2md.parsers.profile import ProfileParser
from gitlab2md.parsers.projects import ProjectsParser
from gitlab2md.parsers.snippets import SnippetsParser
from gitlab2md.parsers.starred import StarredProjectsParser

# =============================================================================
# BaseParser Tests
# =============================================================================


class TestBaseParser:
    """Tests for BaseParser utility methods."""

    @pytest.fixture
    def parser(self):
        return BaseParser()

    def test_format_date_iso_format(self, parser):
        """Test date formatting from ISO format."""
        result = parser._format_date("2024-01-15T10:30:00Z")
        assert result == "Jan 2024"

    def test_format_date_none(self, parser):
        """Test date formatting returns None for None input."""
        assert parser._format_date(None) is None

    def test_format_date_invalid(self, parser):
        """Test date formatting handles invalid dates."""
        result = parser._format_date("not-a-date")
        assert result == "not-a-date"  # Returns original on failure

    def test_format_datetime_iso_format(self, parser):
        """Test datetime formatting from ISO format."""
        result = parser._format_datetime("2024-01-15T10:30:00Z")
        assert result == "2024-01-15 10:30"

    def test_format_datetime_none(self, parser):
        """Test datetime formatting returns None for None input."""
        assert parser._format_datetime(None) is None

    def test_safe_get_single_key(self, parser):
        """Test safe_get with single key."""
        data = {"key": "value"}
        assert parser._safe_get(data, "key") == "value"

    def test_safe_get_nested_keys(self, parser):
        """Test safe_get with nested keys."""
        data = {"outer": {"inner": "value"}}
        assert parser._safe_get(data, "outer", "inner") == "value"

    def test_safe_get_missing_key(self, parser):
        """Test safe_get with missing key returns default."""
        data = {"key": "value"}
        assert parser._safe_get(data, "missing") is None
        assert parser._safe_get(data, "missing", default="default") == "default"

    def test_safe_get_deeply_nested_missing(self, parser):
        """Test safe_get with deeply nested missing key."""
        data = {"outer": {"inner": "value"}}
        assert parser._safe_get(data, "outer", "missing", "deep") is None


# =============================================================================
# ProfileParser Tests
# =============================================================================


class TestProfileParser:
    """Tests for ProfileParser."""

    @pytest.fixture
    def parser(self):
        return ProfileParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "profile"

    def test_parse_complete_profile(self, parser):
        """Test parsing complete profile data."""
        raw_data = {
            "username": "testuser",
            "profile": [
                {
                    "username": "testuser",
                    "name": "Test User",
                    "bio": "A developer",
                    "location": "NYC",
                    "website_url": "https://test.dev",
                    "organization": "TestCorp",
                    "job_title": "Engineer",
                    "state": "active",
                    "created_at": "2020-01-15T10:00:00Z",
                    "web_url": "https://gitlab.com/testuser",
                }
            ],
        }

        result = parser.parse(raw_data)

        assert result["username"] == "testuser"
        assert result["name"] == "Test User"
        assert result["bio"] == "A developer"
        assert result["location"] == "NYC"
        assert result["organization"] == "TestCorp"
        assert result["created_at"] == "Jan 2020"

    def test_parse_empty_profile(self, parser):
        """Test parsing empty profile data."""
        raw_data = {"username": "testuser", "profile": []}

        result = parser.parse(raw_data)

        assert result["username"] == "testuser"
        assert result["name"] is None

    def test_parse_fallback_username(self, parser):
        """Test username fallback to raw_data when not in profile."""
        raw_data = {"username": "fallback", "profile": [{}]}

        result = parser.parse(raw_data)

        assert result["username"] == "fallback"


# =============================================================================
# ProjectsParser Tests
# =============================================================================


class TestProjectsParser:
    """Tests for ProjectsParser."""

    @pytest.fixture
    def parser(self):
        return ProjectsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "projects"

    def test_parse_projects(self, parser):
        """Test parsing projects data."""
        raw_data = {
            "projects": [
                {
                    "name": "project-a",
                    "path_with_namespace": "user/project-a",
                    "description": "Project A description",
                    "visibility": "public",
                    "star_count": 10,
                    "forks_count": 2,
                    "web_url": "https://gitlab.com/user/project-a",
                    "topics": ["python", "cli"],
                },
                {
                    "name": "project-b",
                    "path_with_namespace": "user/project-b",
                    "description": "Project B description",
                    "visibility": "private",
                    "star_count": 5,
                },
            ]
        }

        result = parser.parse(raw_data)

        assert len(result) == 2
        # Should be sorted by stars descending
        assert result[0]["name"] == "project-a"
        assert result[0]["stars"] == 10
        assert result[0]["topics"] == ["python", "cli"]

    def test_parse_skips_forks(self, parser):
        """Test that forked projects are skipped."""
        raw_data = {
            "projects": [
                {"name": "original", "star_count": 5},
                {"name": "fork", "star_count": 0, "forked_from_project": {"id": 123}},
            ]
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["name"] == "original"

    def test_parse_empty_projects(self, parser):
        """Test parsing empty projects list."""
        raw_data = {"projects": []}

        result = parser.parse(raw_data)

        assert result == []

    def test_parse_sorted_by_stars(self, parser):
        """Test projects are sorted by stars descending."""
        raw_data = {
            "projects": [
                {"name": "low", "star_count": 1},
                {"name": "high", "star_count": 100},
                {"name": "medium", "star_count": 50},
            ]
        }

        result = parser.parse(raw_data)

        assert result[0]["name"] == "high"
        assert result[1]["name"] == "medium"
        assert result[2]["name"] == "low"


# =============================================================================
# MemberProjectsParser Tests
# =============================================================================


class TestMemberProjectsParser:
    """Tests for MemberProjectsParser."""

    @pytest.fixture
    def parser(self):
        return MemberProjectsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "member_projects"

    def test_parse_member_projects(self, parser):
        """Test parsing member projects."""
        raw_data = {
            "username": "testuser",
            "member_projects": [
                {
                    "name": "team-project",
                    "path_with_namespace": "team/team-project",
                    "owner": {"username": "teamlead"},
                    "star_count": 25,
                },
            ],
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["name"] == "team-project"

    def test_parse_excludes_own_projects(self, parser):
        """Test that user's own projects are excluded."""
        raw_data = {
            "username": "testuser",
            "member_projects": [
                {
                    "name": "own-project",
                    "namespace": {"path": "testuser", "name": "testuser"},
                },
                {"name": "team-project", "namespace": {"path": "team", "name": "Team"}},
            ],
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["name"] == "team-project"


# =============================================================================
# MergeRequestsParser Tests
# =============================================================================


class TestMergeRequestsParser:
    """Tests for MergeRequestsParser."""

    @pytest.fixture
    def parser(self):
        return MergeRequestsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "merge_requests"

    def test_parse_merge_requests(self, parser):
        """Test parsing merge requests."""
        raw_data = {
            "merge_requests": [
                {
                    "title": "Fix bug",
                    "state": "merged",
                    "web_url": "https://gitlab.com/project/-/mr/1",
                    "references": {"full": "group/project!1"},
                    "created_at": "2024-01-10T10:00:00Z",
                    "merged_at": "2024-01-12T15:00:00Z",
                },
                {
                    "title": "Add feature",
                    "state": "opened",
                    "references": {"full": "group/project!2"},
                },
                {
                    "title": "Rejected",
                    "state": "closed",
                    "references": {"full": "other/project!1"},
                },
            ]
        }

        result = parser.parse(raw_data)

        assert result["total"] == 3
        assert result["by_state"]["merged"] == 1
        assert result["by_state"]["opened"] == 1
        assert result["by_state"]["closed"] == 1
        assert "group/project" in result["by_project"]

    def test_parse_empty_merge_requests(self, parser):
        """Test parsing empty merge requests."""
        raw_data = {"merge_requests": []}

        result = parser.parse(raw_data)

        assert result["total"] == 0
        assert result["by_state"] == {}
        assert result["recent"] == []

    def test_parse_recent_limited_to_max(self, parser):
        """Test that recent MRs are limited to MAX_RECENT_ITEMS."""
        from gitlab2md.constants import MAX_RECENT_ITEMS

        raw_data = {
            "merge_requests": [
                {
                    "title": f"MR {i}",
                    "state": "merged",
                    "references": {"full": f"p!{i}"},
                }
                for i in range(30)
            ]
        }

        result = parser.parse(raw_data)

        assert len(result["recent"]) == MAX_RECENT_ITEMS


# =============================================================================
# EventsParser Tests
# =============================================================================


class TestEventsParser:
    """Tests for EventsParser."""

    @pytest.fixture
    def parser(self):
        return EventsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "events"

    def test_parse_events(self, parser):
        """Test parsing events."""
        raw_data = {
            "events": [
                {"action_name": "pushed to", "project": {"path_with_namespace": "a/b"}},
                {"action_name": "pushed to", "project": {"path_with_namespace": "a/b"}},
                {"action_name": "opened", "project": {"path_with_namespace": "c/d"}},
            ]
        }

        result = parser.parse(raw_data)

        assert result["total_events"] == 3
        assert result["action_types"]["pushed to"] == 2
        assert result["action_types"]["opened"] == 1
        assert "a/b" in result["active_projects"]

    def test_parse_empty_events(self, parser):
        """Test parsing empty events."""
        raw_data = {"events": []}

        result = parser.parse(raw_data)

        assert result["total_events"] == 0
        assert result["action_types"] == {}


# =============================================================================
# GroupsParser Tests
# =============================================================================


class TestGroupsParser:
    """Tests for GroupsParser."""

    @pytest.fixture
    def parser(self):
        return GroupsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "group_contributions"

    def test_parse_group_contributions(self, parser):
        """Test parsing group contributions."""
        raw_data = {
            "group_contributions": {
                "mygroup": {
                    "total_commits": 50,
                    "projects": [
                        {"name": "mygroup/project1", "commits": 30},
                        {"name": "mygroup/project2", "commits": 20},
                    ],
                }
            }
        }

        result = parser.parse(raw_data)

        assert "mygroup" in result
        assert result["mygroup"]["total_commits"] == 50
        assert len(result["mygroup"]["projects"]) == 2

    def test_parse_empty_group_contributions(self, parser):
        """Test parsing empty group contributions."""
        raw_data = {"group_contributions": {}}

        result = parser.parse(raw_data)

        assert result == {}

    def test_parse_missing_group_contributions(self, parser):
        """Test parsing when group_contributions is missing."""
        raw_data = {}

        result = parser.parse(raw_data)

        assert result == {}


# =============================================================================
# IssuesParser Tests
# =============================================================================


class TestIssuesParser:
    """Tests for IssuesParser."""

    @pytest.fixture
    def parser(self):
        return IssuesParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "issues"

    def test_parse_issues(self, parser):
        """Test parsing issues."""
        raw_data = {
            "issues": [
                {
                    "title": "Bug report",
                    "state": "opened",
                    "web_url": "https://gitlab.com/project/-/issues/1",
                    "references": {"full": "group/project#1"},
                    "labels": ["bug", "critical"],
                    "created_at": "2024-01-10T10:00:00Z",
                },
                {
                    "title": "Feature request",
                    "state": "closed",
                    "references": {"full": "group/project#2"},
                    "labels": ["enhancement"],
                },
            ]
        }

        result = parser.parse(raw_data)

        assert result["total"] == 2
        assert result["by_state"]["opened"] == 1
        assert result["by_state"]["closed"] == 1
        assert "group/project" in result["by_project"]
        assert "bug" in result["top_labels"]

    def test_parse_empty_issues(self, parser):
        """Test parsing empty issues."""
        raw_data = {"issues": []}

        result = parser.parse(raw_data)

        assert result["total"] == 0
        assert result["recent"] == []


# =============================================================================
# StarredProjectsParser Tests
# =============================================================================


class TestStarredProjectsParser:
    """Tests for StarredProjectsParser."""

    @pytest.fixture
    def parser(self):
        return StarredProjectsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "starred_projects"

    def test_parse_starred_projects(self, parser):
        """Test parsing starred projects."""
        raw_data = {
            "starred_projects": [
                {
                    "name": "awesome-project",
                    "path_with_namespace": "org/awesome-project",
                    "description": "An awesome project",
                    "visibility": "public",
                    "star_count": 100,
                    "web_url": "https://gitlab.com/org/awesome-project",
                },
            ]
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["name"] == "awesome-project"
        assert result[0]["stars"] == 100

    def test_parse_empty_starred(self, parser):
        """Test parsing empty starred projects."""
        raw_data = {"starred_projects": []}

        result = parser.parse(raw_data)

        assert result == []


# =============================================================================
# SnippetsParser Tests
# =============================================================================


class TestSnippetsParser:
    """Tests for SnippetsParser."""

    @pytest.fixture
    def parser(self):
        return SnippetsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "snippets"

    def test_parse_snippets(self, parser):
        """Test parsing snippets."""
        raw_data = {
            "snippets": [
                {
                    "title": "My snippet",
                    "description": "A helpful snippet",
                    "visibility": "public",
                    "web_url": "https://gitlab.com/snippets/123",
                    "file_name": "script.py",
                    "created_at": "2024-01-10T10:00:00Z",
                },
            ]
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["title"] == "My snippet"
        assert result[0]["file_name"] == "script.py"

    def test_parse_empty_snippets(self, parser):
        """Test parsing empty snippets."""
        raw_data = {"snippets": []}

        result = parser.parse(raw_data)

        assert result == []


# =============================================================================
# SSHKeysParser Tests
# =============================================================================


class TestSSHKeysParser:
    """Tests for SSHKeysParser."""

    @pytest.fixture
    def parser(self):
        return SSHKeysParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "ssh_keys"

    def test_parse_ssh_keys(self, parser):
        """Test parsing SSH keys."""
        raw_data = {
            "ssh_keys": [
                {
                    "title": "My laptop",
                    "created_at": "2024-01-10T10:00:00Z",
                    "expires_at": "2025-01-10T10:00:00Z",
                    "usage_type": "auth_and_signing",
                },
            ]
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["title"] == "My laptop"

    def test_parse_empty_ssh_keys(self, parser):
        """Test parsing empty SSH keys."""
        raw_data = {"ssh_keys": []}

        result = parser.parse(raw_data)

        assert result == []


# =============================================================================
# GPGKeysParser Tests
# =============================================================================


class TestGPGKeysParser:
    """Tests for GPGKeysParser."""

    @pytest.fixture
    def parser(self):
        return GPGKeysParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "gpg_keys"

    def test_parse_gpg_keys(self, parser):
        """Test parsing GPG keys."""
        raw_data = {
            "gpg_keys": [
                {
                    "key_id": "ABC123DEF456",
                    "created_at": "2024-01-10T10:00:00Z",
                },
            ]
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["key_id"] == "ABC123DEF456"

    def test_parse_empty_gpg_keys(self, parser):
        """Test parsing empty GPG keys."""
        raw_data = {"gpg_keys": []}

        result = parser.parse(raw_data)

        assert result == []


# =============================================================================
# MembershipsParser Tests
# =============================================================================


class TestMembershipsParser:
    """Tests for MembershipsParser."""

    @pytest.fixture
    def parser(self):
        return MembershipsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "memberships"

    def test_parse_memberships(self, parser):
        """Test parsing memberships."""
        raw_data = {
            "memberships": [
                {
                    "source_type": "Namespace",
                    "source_name": "My Group",
                    "source_full_path": "my-group",
                    "access_level": 30,
                    "created_at": "2024-01-10T10:00:00Z",
                },
                {
                    "source_type": "Project",
                    "source_name": "My Project",
                    "source_full_path": "my-group/my-project",
                    "access_level": 40,
                },
            ]
        }

        result = parser.parse(raw_data)

        assert result["total"] == 2
        assert len(result["groups"]) == 1
        assert len(result["projects"]) == 1
        assert result["groups"][0]["access_level"] == "Developer"
        assert result["projects"][0]["access_level"] == "Maintainer"

    def test_parse_empty_memberships(self, parser):
        """Test parsing empty memberships."""
        raw_data = {"memberships": []}

        result = parser.parse(raw_data)

        assert result["total"] == 0
        assert result["groups"] == []
        assert result["projects"] == []


# =============================================================================
# ContributedProjectsParser Tests
# =============================================================================


class TestContributedProjectsParser:
    """Tests for ContributedProjectsParser."""

    @pytest.fixture
    def parser(self):
        return ContributedProjectsParser()

    def test_section_key(self, parser):
        """Test section key is correct."""
        assert parser.section_key == "contributed_projects"

    def test_parse_contributed_projects(self, parser):
        """Test parsing contributed projects."""
        raw_data = {
            "contributed_projects": [
                {
                    "name": "open-source-project",
                    "path_with_namespace": "org/open-source-project",
                    "description": "A project I contributed to",
                    "visibility": "public",
                    "star_count": 500,
                    "web_url": "https://gitlab.com/org/open-source-project",
                },
            ]
        }

        result = parser.parse(raw_data)

        assert len(result) == 1
        assert result[0]["name"] == "open-source-project"
        assert result[0]["stars"] == 500

    def test_parse_empty_contributed(self, parser):
        """Test parsing empty contributed projects."""
        raw_data = {"contributed_projects": []}

        result = parser.parse(raw_data)

        assert result == []
