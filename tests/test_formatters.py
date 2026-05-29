"""Tests for all formatters."""

import pytest

from gitlab2md.formatters.base import BaseFormatter
from gitlab2md.formatters.contributed import ContributedProjectsFormatter
from gitlab2md.formatters.events import EventsFormatter
from gitlab2md.formatters.groups import GroupsFormatter
from gitlab2md.formatters.issues import IssuesFormatter
from gitlab2md.formatters.keys import GPGKeysFormatter, SSHKeysFormatter
from gitlab2md.formatters.member_projects import MemberProjectsFormatter
from gitlab2md.formatters.memberships import MembershipsFormatter
from gitlab2md.formatters.merge_requests import MergeRequestsFormatter
from gitlab2md.formatters.profile import ProfileFormatter
from gitlab2md.formatters.projects import ProjectsFormatter
from gitlab2md.formatters.snippets import SnippetsFormatter
from gitlab2md.formatters.starred import StarredProjectsFormatter

# =============================================================================
# BaseFormatter Tests
# =============================================================================


class ConcreteFormatter(BaseFormatter):
    """Concrete implementation for testing base class methods."""

    @property
    def section_key(self) -> str:
        return "test"

    @property
    def output_filename(self) -> str:
        return "test.md"

    def format(self, data):
        return ""


class TestBaseFormatter:
    """Tests for BaseFormatter utility methods."""

    @pytest.fixture
    def formatter(self):
        return ConcreteFormatter()

    def test_escape_md_pipes(self, formatter):
        """Test escaping pipe characters."""
        result = formatter._escape_md("text | with | pipes")
        assert result == "text \\| with \\| pipes"

    def test_escape_md_special_chars(self, formatter):
        """Test escaping GFM special characters."""
        result = formatter._escape_md("* _ ` [ ]")
        assert result == "\\* \\_ \\` \\[ \\]"

    def test_escape_md_backslash_first(self, formatter):
        """Test backslash is escaped first to prevent double-escaping."""
        result = formatter._escape_md("\\*")
        assert result == "\\\\\\*"

    def test_escape_md_does_not_escape_dot_in_version(self, formatter):
        """Test that dots in version numbers are preserved."""
        result = formatter._escape_md("v1.2.3")
        assert result == "v1.2.3"

    def test_escape_md_does_not_escape_parentheses(self, formatter):
        """Test that parentheses in normal text are preserved."""
        result = formatter._escape_md("function(arg1, arg2)")
        assert result == "function(arg1, arg2)"

    def test_escape_md_does_not_escape_plus_minus(self, formatter):
        """Test that + and - in normal text are preserved."""
        result = formatter._escape_md("C++ and up-to-date")
        assert result == "C++ and up-to-date"

    def test_escape_md_does_not_escape_braces(self, formatter):
        """Test that curly braces in normal text are preserved."""
        result = formatter._escape_md("{key: value}")
        assert result == "{key: value}"

    def test_escape_md_does_not_escape_exclamation(self, formatter):
        """Test that exclamation marks are preserved."""
        result = formatter._escape_md("Hello! World!")
        assert result == "Hello! World!"

    def test_escape_md_none(self, formatter):
        """Test escaping None returns empty string."""
        assert formatter._escape_md(None) == ""

    def test_escape_md_empty(self, formatter):
        """Test escaping empty string."""
        assert formatter._escape_md("") == ""

    def test_make_link_with_url(self, formatter):
        """Test making link with URL."""
        result = formatter._make_link("text", "https://example.com")
        assert result == "[text](https://example.com)"

    def test_make_link_without_url(self, formatter):
        """Test making link without URL returns just text."""
        result = formatter._make_link("text", None)
        assert result == "text"

    def test_make_link_empty_url(self, formatter):
        """Test making link with empty URL returns just text."""
        result = formatter._make_link("text", "")
        assert result == "text"

    def test_truncate_short_text(self, formatter):
        """Test truncate doesn't modify short text."""
        result = formatter._truncate("short text", 100)
        assert result == "short text"

    def test_truncate_long_text(self, formatter):
        """Test truncate adds ellipsis to long text."""
        result = formatter._truncate("a" * 200, 100)
        assert len(result) == 100
        assert result.endswith("...")

    def test_truncate_none(self, formatter):
        """Test truncate None returns empty string."""
        assert formatter._truncate(None, 100) == ""

    def test_truncate_default_length(self, formatter):
        """Test truncate uses default max length."""
        result = formatter._truncate("a" * 200)
        assert len(result) == 100  # default max_len


# =============================================================================
# ProfileFormatter Tests
# =============================================================================


class TestProfileFormatter:
    """Tests for ProfileFormatter."""

    @pytest.fixture
    def formatter(self):
        return ProfileFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "profile"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "profile.md"

    def test_format_complete_profile(self, formatter):
        """Test formatting complete profile."""
        data = {
            "username": "testuser",
            "name": "Test User",
            "bio": "A developer",
            "location": "NYC",
            "organization": "TestCorp",
            "job_title": "Engineer",
            "website": "https://test.dev",
            "created_at": "Jan 2020",
            "web_url": "https://gitlab.com/testuser",
        }

        result = formatter.format(data)

        assert "# GitLab Profile: testuser" in result
        assert "**Test User**" in result
        assert "> A developer" in result
        assert "**Job Title:** Engineer" in result
        assert "**Location:** NYC" in result
        assert "**Organization:** TestCorp" in result
        assert "**Member since:** Jan 2020" in result
        assert "https://gitlab.com/testuser" in result

    def test_format_minimal_profile(self, formatter):
        """Test formatting minimal profile."""
        data = {"username": "testuser"}

        result = formatter.format(data)

        assert "# GitLab Profile: testuser" in result

    def test_format_missing_username(self, formatter):
        """Test formatting with missing username uses 'Unknown'."""
        data = {}

        result = formatter.format(data)

        assert "Unknown" in result


# =============================================================================
# ProjectsFormatter Tests
# =============================================================================


class TestProjectsFormatter:
    """Tests for ProjectsFormatter."""

    @pytest.fixture
    def formatter(self):
        return ProjectsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "projects"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "projects.md"

    def test_format_projects(self, formatter):
        """Test formatting projects."""
        data = [
            {
                "name": "my-project",
                "url": "https://gitlab.com/user/my-project",
                "description": "A test project",
                "visibility": "public",
                "stars": 10,
                "topics": ["python", "cli"],
            }
        ]

        result = formatter.format(data)

        assert "# Owned Projects (1)" in result
        assert "[my-project]" in result
        assert "A test project" in result
        assert "**Visibility:** public" in result
        assert "**Stars:** 10" in result
        assert "python" in result

    def test_format_empty_projects(self, formatter):
        """Test formatting empty projects list."""
        result = formatter.format([])

        assert "No public projects" in result

    def test_format_truncates_description(self, formatter):
        """Test that long descriptions are truncated."""
        data = [
            {
                "name": "project",
                "description": "A" * 300,
                "visibility": "public",
                "stars": 0,
            }
        ]

        result = formatter.format(data)

        assert "..." in result


# =============================================================================
# MemberProjectsFormatter Tests
# =============================================================================


class TestMemberProjectsFormatter:
    """Tests for MemberProjectsFormatter."""

    @pytest.fixture
    def formatter(self):
        return MemberProjectsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "member_projects"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "member_projects.md"

    def test_format_member_projects(self, formatter):
        """Test formatting member projects."""
        data = [
            {
                "name": "team-project",
                "url": "https://gitlab.com/team/project",
                "description": "Team project",
                "visibility": "internal",
                "stars": 25,
            }
        ]

        result = formatter.format(data)

        assert "Member Projects" in result
        assert "team-project" in result


# =============================================================================
# MergeRequestsFormatter Tests
# =============================================================================


class TestMergeRequestsFormatter:
    """Tests for MergeRequestsFormatter."""

    @pytest.fixture
    def formatter(self):
        return MergeRequestsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "merge_requests"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "merge_requests.md"

    def test_format_merge_requests(self, formatter):
        """Test formatting merge requests."""
        data = {
            "total": 5,
            "by_state": {"merged": 3, "opened": 1, "closed": 1},
            "by_project": {"group/project": 5},
            "recent": [
                {
                    "title": "Fix bug",
                    "state": "merged",
                    "url": "https://gitlab.com/project/-/mr/1",
                    "project": "group/project",
                }
            ],
        }

        result = formatter.format(data)

        assert "# Merge Requests (5 total)" in result
        assert "**Merged:** 3" in result
        assert "**Opened:** 1" in result
        assert "group/project" in result
        assert "Fix bug" in result

    def test_format_status_emojis(self, formatter):
        """Test that status emojis are used."""
        data = {
            "total": 3,
            "by_state": {},
            "by_project": {},
            "recent": [
                {"title": "Merged", "state": "merged", "project": "p"},
                {"title": "Closed", "state": "closed", "project": "p"},
                {"title": "Open", "state": "opened", "project": "p"},
            ],
        }

        result = formatter.format(data)

        # Check for status indicators (unicode checkmark, x, circle)
        assert "Merged" in result
        assert "Closed" in result
        assert "Open" in result

    def test_format_empty_merge_requests(self, formatter):
        """Test formatting empty merge requests."""
        data = {"total": 0, "by_state": {}, "by_project": {}, "recent": []}

        result = formatter.format(data)

        assert "# Merge Requests (0 total)" in result


# =============================================================================
# EventsFormatter Tests
# =============================================================================


class TestEventsFormatter:
    """Tests for EventsFormatter."""

    @pytest.fixture
    def formatter(self):
        return EventsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "events"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "activity.md"

    def test_format_events(self, formatter):
        """Test formatting events."""
        data = {
            "total_events": 10,
            "action_types": {"pushed to": 5, "opened": 3, "commented": 2},
            "active_projects": {"group/project": 8, "other/project": 2},
        }

        result = formatter.format(data)

        assert "# Recent Activity" in result
        assert "Total events: 10" in result
        assert "**pushed to:** 5" in result
        assert "group/project" in result

    def test_format_empty_events(self, formatter):
        """Test formatting empty events."""
        data = {"total_events": 0, "action_types": {}, "active_projects": {}}

        result = formatter.format(data)

        assert "Total events: 0" in result


# =============================================================================
# GroupsFormatter Tests
# =============================================================================


class TestGroupsFormatter:
    """Tests for GroupsFormatter."""

    @pytest.fixture
    def formatter(self):
        return GroupsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "group_contributions"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "groups.md"

    def test_format_group_contributions(self, formatter):
        """Test formatting group contributions."""
        data = {
            "mygroup": {
                "total_commits": 50,
                "projects": [
                    {
                        "name": "mygroup/project1",
                        "commits": 30,
                        "url": "https://gitlab.com/mygroup/project1",
                    },
                    {
                        "name": "mygroup/project2",
                        "commits": 20,
                        "url": "https://gitlab.com/mygroup/project2",
                    },
                ],
            }
        }

        result = formatter.format(data)

        assert "# Group Contributions" in result
        assert "## mygroup" in result
        assert "**Total commits:** 50" in result
        assert "mygroup/project1" in result
        assert "30 commits" in result

    def test_format_empty_contributions(self, formatter):
        """Test formatting empty group contributions."""
        result = formatter.format({})

        assert "No group contributions tracked" in result


# =============================================================================
# IssuesFormatter Tests
# =============================================================================


class TestIssuesFormatter:
    """Tests for IssuesFormatter."""

    @pytest.fixture
    def formatter(self):
        return IssuesFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "issues"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "issues.md"

    def test_format_issues(self, formatter):
        """Test formatting issues."""
        data = {
            "total": 5,
            "by_state": {"opened": 3, "closed": 2},
            "by_project": {"group/project": 5},
            "top_labels": {"bug": 3, "enhancement": 2},
            "recent": [
                {
                    "title": "Bug report",
                    "state": "opened",
                    "url": "https://gitlab.com/project/-/issues/1",
                    "project": "group/project",
                    "confidential": False,
                }
            ],
        }

        result = formatter.format(data)

        assert "# Issues (5 total)" in result
        assert "**Opened:** 3" in result
        assert "group/project" in result
        assert "Bug report" in result

    def test_format_empty_issues(self, formatter):
        """Test formatting empty issues."""
        data = {
            "total": 0,
            "by_state": {},
            "by_project": {},
            "top_labels": {},
            "recent": [],
        }

        result = formatter.format(data)

        assert "# Issues (0 total)" in result


# =============================================================================
# StarredProjectsFormatter Tests
# =============================================================================


class TestStarredProjectsFormatter:
    """Tests for StarredProjectsFormatter."""

    @pytest.fixture
    def formatter(self):
        return StarredProjectsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "starred_projects"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "starred.md"

    def test_format_starred_projects(self, formatter):
        """Test formatting starred projects."""
        data = [
            {
                "name": "awesome-project",
                "url": "https://gitlab.com/org/awesome-project",
                "description": "An awesome project",
                "stars": 100,
                "topics": ["python", "cli"],
            }
        ]

        result = formatter.format(data)

        assert "# Starred Projects (1)" in result
        assert "awesome-project" in result
        assert "**Stars:** 100" in result

    def test_format_empty_starred(self, formatter):
        """Test formatting empty starred projects."""
        result = formatter.format([])

        assert "No starred projects" in result


# =============================================================================
# SnippetsFormatter Tests
# =============================================================================


class TestSnippetsFormatter:
    """Tests for SnippetsFormatter."""

    @pytest.fixture
    def formatter(self):
        return SnippetsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "snippets"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "snippets.md"

    def test_format_snippets(self, formatter):
        """Test formatting snippets."""
        data = [
            {
                "title": "My snippet",
                "description": "A helpful snippet",
                "visibility": "public",
                "url": "https://gitlab.com/snippets/123",
                "file_name": "script.py",
                "created_at": "Jan 2024",
            }
        ]

        result = formatter.format(data)

        assert "# Snippets (1)" in result
        assert "My snippet" in result
        assert "**File:** `script.py`" in result

    def test_format_empty_snippets(self, formatter):
        """Test formatting empty snippets."""
        result = formatter.format([])

        assert "No snippets" in result


# =============================================================================
# SSHKeysFormatter Tests
# =============================================================================


class TestSSHKeysFormatter:
    """Tests for SSHKeysFormatter."""

    @pytest.fixture
    def formatter(self):
        return SSHKeysFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "ssh_keys"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "ssh_keys.md"

    def test_format_ssh_keys(self, formatter):
        """Test formatting SSH keys."""
        data = [
            {
                "title": "My laptop",
                "created_at": "Jan 2024",
                "expires_at": "Jan 2025",
                "usage_type": "auth",
            }
        ]

        result = formatter.format(data)

        assert "# SSH Keys (1)" in result
        assert "## My laptop" in result
        assert "**Created:** Jan 2024" in result

    def test_format_empty_ssh_keys(self, formatter):
        """Test formatting empty SSH keys."""
        result = formatter.format([])

        assert "No SSH keys configured" in result


# =============================================================================
# GPGKeysFormatter Tests
# =============================================================================


class TestGPGKeysFormatter:
    """Tests for GPGKeysFormatter."""

    @pytest.fixture
    def formatter(self):
        return GPGKeysFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "gpg_keys"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "gpg_keys.md"

    def test_format_gpg_keys(self, formatter):
        """Test formatting GPG keys."""
        data = [
            {
                "key_id": "ABC123",
                "created_at": "Jan 2024",
            }
        ]

        result = formatter.format(data)

        assert "# GPG Keys (1)" in result
        assert "## Key: ABC123" in result

    def test_format_empty_gpg_keys(self, formatter):
        """Test formatting empty GPG keys."""
        result = formatter.format([])

        assert "No GPG keys configured" in result


# =============================================================================
# MembershipsFormatter Tests
# =============================================================================


class TestMembershipsFormatter:
    """Tests for MembershipsFormatter."""

    @pytest.fixture
    def formatter(self):
        return MembershipsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "memberships"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "memberships.md"

    def test_format_memberships(self, formatter):
        """Test formatting memberships."""
        data = {
            "total": 2,
            "groups": [
                {
                    "name": "My Group",
                    "full_path": "my-group",
                    "access_level": "Developer",
                }
            ],
            "projects": [
                {
                    "name": "My Project",
                    "full_path": "my-group/my-project",
                    "access_level": "Maintainer",
                }
            ],
            "by_access_level": {"Developer": 1, "Maintainer": 1},
        }

        result = formatter.format(data)

        assert "# Memberships (2 total)" in result
        assert "## Groups (1)" in result
        assert "## Projects (1)" in result
        assert "My Group" in result

    def test_format_empty_memberships(self, formatter):
        """Test formatting empty memberships."""
        data = {"total": 0, "groups": [], "projects": [], "by_access_level": {}}

        result = formatter.format(data)

        assert "No memberships found" in result


# =============================================================================
# ContributedProjectsFormatter Tests
# =============================================================================


class TestContributedProjectsFormatter:
    """Tests for ContributedProjectsFormatter."""

    @pytest.fixture
    def formatter(self):
        return ContributedProjectsFormatter()

    def test_section_key(self, formatter):
        """Test section key is correct."""
        assert formatter.section_key == "contributed_projects"

    def test_output_filename(self, formatter):
        """Test output filename is correct."""
        assert formatter.output_filename == "contributions.md"

    def test_format_contributed_projects(self, formatter):
        """Test formatting contributed projects."""
        data = [
            {
                "name": "open-source-project",
                "url": "https://gitlab.com/org/open-source-project",
                "description": "A project I contributed to",
                "visibility": "public",
                "stars": 500,
                "topics": ["python"],
            }
        ]

        result = formatter.format(data)

        assert "# Contributed Projects (1)" in result
        assert "open-source-project" in result
        assert "**Stars:** 500" in result

    def test_format_empty_contributed(self, formatter):
        """Test formatting empty contributed projects."""
        result = formatter.format([])

        assert "No contributed projects found" in result
