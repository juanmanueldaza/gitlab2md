"""Section parsers for GitLab data."""

from .contributed import ContributedProjectsParser
from .events import EventsParser
from .groups import GroupsParser
from .issues import IssuesParser
from .keys import GPGKeysParser, SSHKeysParser
from .member_projects import MemberProjectsParser
from .memberships import MembershipsParser
from .merge_requests import MergeRequestsParser
from .profile import ProfileParser
from .projects import ProjectsParser
from .snippets import SnippetsParser
from .starred import StarredProjectsParser

__all__ = [
    "ProfileParser",
    "ProjectsParser",
    "MemberProjectsParser",
    "MergeRequestsParser",
    "EventsParser",
    "GroupsParser",
    "IssuesParser",
    "StarredProjectsParser",
    "SnippetsParser",
    "SSHKeysParser",
    "GPGKeysParser",
    "MembershipsParser",
    "ContributedProjectsParser",
]
