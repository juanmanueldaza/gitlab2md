"""GitLab data extraction via glab CLI."""

import json
import logging
import subprocess
from typing import Any

from .constants import DEFAULT_PAGE_SIZE
from .validation import validate_gitlab_name


class GitLabExtractor:
    """Extract GitLab data using the glab CLI.

    Security features:
    - Input validation for usernames and group names
    - Safe error messages (no credential leakage)
    - Robust error handling
    """

    def __init__(self, groups: list[str] | None = None) -> None:
        self._groups = groups or []
        self._profile_cache: dict[str, list[dict[str, Any]]] = {}
        # Validate group names at initialization
        for group in self._groups:
            validate_gitlab_name(group, "group")

    def _run_glab(self, *args: str) -> str:
        """Run glab CLI command and return output.

        Raises:
            RuntimeError: If command fails (with safe error message).
        """
        cmd = ["glab", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # Safe error messages - don't expose raw stderr
            stderr = result.stderr.strip().lower()
            if "rate limit" in stderr:
                raise RuntimeError("GitLab API rate limit exceeded. Try again later.")
            if "not found" in stderr or "404" in stderr:
                raise RuntimeError("User or resource not found on GitLab.")
            if "unauthorized" in stderr or "401" in stderr or "403" in stderr:
                raise RuntimeError(
                    "Authentication failed. Run 'glab auth login' to authenticate."
                )
            # Generic error without exposing internals
            raise RuntimeError("GitLab CLI command failed. Check authentication.")
        return result.stdout

    def _run_glab_json(self, *args: str) -> Any:
        """Run glab CLI command and parse JSON output."""
        output = self._run_glab(*args)
        return json.loads(output) if output.strip() else {}

    def _safe_extract_list(self, *args: str) -> list[dict[str, Any]]:
        """Extract list data with error handling.

        DRY helper that handles the common pattern of extracting
        a list from the API with fallback to empty list on error.
        """
        try:
            result = self._run_glab_json(*args)
            return result if isinstance(result, list) else []
        except Exception as e:
            logging.warning("Failed to extract list data: %s", e)
            return []

    def _safe_extract_dict(self, *args: str) -> dict[str, Any]:
        """Extract dict data with error handling.

        DRY helper for extracting dict responses.
        """
        try:
            result = self._run_glab_json(*args)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logging.warning("Failed to extract dict data: %s", e)
            return {}

    def extract(self, username: str) -> dict[str, Any]:
        """Extract all data for a GitLab user.

        Args:
            username: GitLab username to extract data for.

        Returns:
            Dictionary with all extracted data sections.

        Raises:
            ValueError: If username is invalid.
        """
        validate_gitlab_name(username, "username")

        data: dict[str, Any] = {"username": username}

        # User info
        data["profile"] = self._get_profile(username)

        # Projects owned
        data["projects"] = self._get_projects(username)

        # Projects where user is a member
        data["member_projects"] = self._get_member_projects()

        # Merge requests
        data["merge_requests"] = self._get_merge_requests(username)

        # User events
        data["events"] = self._get_events(username)

        # Issues authored by user
        data["issues"] = self._get_issues(username)

        # Starred projects
        data["starred_projects"] = self._get_starred_projects(username)

        # User snippets
        data["snippets"] = self._get_snippets(username)

        # SSH keys
        data["ssh_keys"] = self._get_ssh_keys(username)

        # GPG keys
        data["gpg_keys"] = self._get_gpg_keys(username)

        # User's group/project memberships
        data["memberships"] = self._get_memberships(username)

        # Contributed projects
        data["contributed_projects"] = self._get_contributed_projects(username)

        # Group contributions if specified
        if self._groups:
            data["group_contributions"] = self._get_group_contributions(username)

        return data

    def _get_profile(self, username: str) -> list[dict[str, Any]]:
        """Get user profile information with caching."""
        if username not in self._profile_cache:
            self._profile_cache[username] = self._safe_extract_list(
                "api", f"/users?username={username}"
            )
        return self._profile_cache[username]

    def _get_projects(self, username: str) -> list[dict[str, Any]]:
        """Get user's owned projects."""
        return self._safe_extract_list(
            "api", f"/users/{username}/projects?per_page={DEFAULT_PAGE_SIZE}"
        )

    def _get_member_projects(self) -> list[dict[str, Any]]:
        """Get projects where user is a member."""
        return self._safe_extract_list(
            "api", f"/projects?membership=true&per_page={DEFAULT_PAGE_SIZE}"
        )

    def _get_merge_requests(self, username: str) -> list[dict[str, Any]]:
        """Get user's merge requests."""
        return self._safe_extract_list(
            "api",
            f"/merge_requests?author_username={username}&scope=all&per_page={DEFAULT_PAGE_SIZE}",
        )

    def _get_events(self, username: str) -> list[dict[str, Any]]:
        """Get user's recent events."""
        return self._safe_extract_list(
            "api", f"/users/{username}/events?per_page={DEFAULT_PAGE_SIZE}"
        )

    def _get_issues(self, username: str) -> list[dict[str, Any]]:
        """Get issues authored by user."""
        return self._safe_extract_list(
            "api",
            f"/issues?author_username={username}&scope=all&per_page={DEFAULT_PAGE_SIZE}",
        )

    def _get_starred_projects(self, username: str) -> list[dict[str, Any]]:
        """Get projects starred by user."""
        return self._safe_extract_list(
            "api", f"/users/{username}/starred_projects?per_page={DEFAULT_PAGE_SIZE}"
        )

    def _get_snippets(self, username: str) -> list[dict[str, Any]]:
        """Get user's snippets."""
        try:
            profile = self._get_profile(username)
            if profile:
                user_id = profile[0].get("id")
                if user_id:
                    return self._safe_extract_list(
                        "api",
                        f"/users/{user_id}/snippets?per_page={DEFAULT_PAGE_SIZE}",
                    )
            return []
        except Exception as e:
            logging.warning("Failed to get snippets for '%s': %s", username, e)
            return []

    def _get_ssh_keys(self, username: str) -> list[dict[str, Any]]:
        """Get user's SSH keys."""
        try:
            profile = self._get_profile(username)
            if profile:
                user_id = profile[0].get("id")
                if user_id:
                    return self._safe_extract_list("api", f"/users/{user_id}/keys")
            return []
        except Exception as e:
            logging.warning("Failed to get SSH keys for '%s': %s", username, e)
            return []

    def _get_gpg_keys(self, username: str) -> list[dict[str, Any]]:
        """Get user's GPG keys."""
        try:
            profile = self._get_profile(username)
            if profile:
                user_id = profile[0].get("id")
                if user_id:
                    return self._safe_extract_list("api", f"/users/{user_id}/gpg_keys")
            return []
        except Exception as e:
            logging.warning("Failed to get GPG keys for '%s': %s", username, e)
            return []

    def _get_memberships(self, username: str) -> list[dict[str, Any]]:
        """Get user's group and project memberships."""
        try:
            profile = self._get_profile(username)
            if profile:
                user_id = profile[0].get("id")
                if user_id:
                    return self._safe_extract_list(
                        "api", f"/users/{user_id}/memberships"
                    )
            return []
        except Exception as e:
            logging.warning("Failed to get memberships for '%s': %s", username, e)
            return []

    def _get_contributed_projects(self, username: str) -> list[dict[str, Any]]:
        """Get projects the user has contributed to."""
        return self._safe_extract_list(
            "api",
            f"/users/{username}/contributed_projects?per_page={DEFAULT_PAGE_SIZE}",
        )

    def _get_group_contributions(self, username: str) -> dict[str, Any]:
        """Get contributions to specified groups."""
        contributions: dict[str, Any] = {}

        # Get user's full name for commit matching
        profile = self._get_profile(username)
        user_name = ""
        if profile:
            user_name = profile[0].get("name", "")

        # Build search terms
        search_terms = [username.lower()]
        if user_name:
            search_terms.append(user_name.lower())
            parts = user_name.lower().split()
            if len(parts) >= 2:
                search_terms.append(parts[-1])

        for group in self._groups:
            try:
                projects = self._safe_extract_list(
                    "api",
                    f"/groups/{group}/projects?include_subgroups=true&per_page={DEFAULT_PAGE_SIZE}",
                )
                if not projects:
                    continue

                group_data: dict[str, Any] = {"projects": [], "total_commits": 0}

                for project in projects:
                    project_id = project.get("id")
                    project_name = project.get("path_with_namespace")

                    commits = self._safe_extract_list(
                        "api",
                        f"/projects/{project_id}/repository/commits?per_page={DEFAULT_PAGE_SIZE}",
                    )
                    if not commits:
                        continue

                    user_commits = self._count_user_commits(commits, search_terms)

                    if user_commits > 0:
                        group_data["projects"].append(
                            {
                                "name": project_name,
                                "commits": user_commits,
                                "url": project.get("web_url"),
                            }
                        )
                        group_data["total_commits"] += user_commits

                if group_data["projects"]:
                    contributions[group] = group_data

            except Exception as e:
                logging.warning(
                    "Failed to get group contributions for '%s': %s", group, e
                )

        return contributions

    def _count_user_commits(
        self, commits: list[dict[str, Any]], search_terms: list[str]
    ) -> int:
        """Count commits matching user's search terms.

        Args:
            commits: List of commit objects.
            search_terms: Lowercase terms to match against author.

        Returns:
            Number of matching commits.
        """
        count = 0
        for commit in commits:
            author_name = (commit.get("author_name") or "").lower()
            author_email = (commit.get("author_email") or "").lower()

            for term in search_terms:
                if term in author_name or term in author_email:
                    count += 1
                    break
        return count


class DictExtractor:
    """Mock extractor for testing."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def extract(self, username: str) -> dict[str, Any]:
        return {**self._data, "username": username}
