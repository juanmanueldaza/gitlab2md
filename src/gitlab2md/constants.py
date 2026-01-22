"""Shared constants for gitlab2md.

Centralizes all magic numbers and configuration values for maintainability.
Following Open/Closed Principle: values can be changed without modifying logic.
"""

# API pagination settings
DEFAULT_PAGE_SIZE = 100

# Display limits for formatted output
DEFAULT_TOP_N = 10  # Top items to show in summaries (labels, projects, etc.)
MAX_RECENT_ITEMS = 15  # Recent MRs, issues, etc. to display
MAX_TOPICS_DISPLAY = 5  # Max topics to show inline

# Text truncation limits
DEFAULT_TRUNCATE_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 150
TITLE_MAX_LENGTH = 60

# Input validation
MAX_NAME_LENGTH = 255  # Max username/group name length

# Access level mappings for GitLab
ACCESS_LEVEL_NAMES = {
    10: "Guest",
    20: "Reporter",
    30: "Developer",
    40: "Maintainer",
    50: "Owner",
}

# Status emoji mappings
MR_STATUS_EMOJI = {"merged": "✓", "closed": "✗", "opened": "○"}
ISSUE_STATUS_EMOJI = {"opened": "○", "closed": "✓"}

# URL security
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}
