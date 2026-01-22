"""Section formatters for GitLab data."""

from .contributed import ContributedProjectsFormatter
from .events import EventsFormatter
from .groups import GroupsFormatter
from .issues import IssuesFormatter
from .keys import GPGKeysFormatter, SSHKeysFormatter
from .member_projects import MemberProjectsFormatter
from .memberships import MembershipsFormatter
from .merge_requests import MergeRequestsFormatter
from .profile import ProfileFormatter
from .projects import ProjectsFormatter
from .snippets import SnippetsFormatter
from .starred import StarredProjectsFormatter

__all__ = [
    "ProfileFormatter",
    "ProjectsFormatter",
    "MemberProjectsFormatter",
    "MergeRequestsFormatter",
    "EventsFormatter",
    "GroupsFormatter",
    "IssuesFormatter",
    "StarredProjectsFormatter",
    "SnippetsFormatter",
    "SSHKeysFormatter",
    "GPGKeysFormatter",
    "MembershipsFormatter",
    "ContributedProjectsFormatter",
]
