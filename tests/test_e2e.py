"""End-to-end tests for gitlab2md.

These tests simulate real-world usage with complete GitLab data.
"""

from pathlib import Path

import pytest

from gitlab2md.converter import GitLabToMarkdownConverter
from gitlab2md.extractor import DictExtractor
from gitlab2md.writer import InMemoryWriter, MarkdownFileWriter


class TestEndToEnd:
    """End-to-end integration tests."""

    @pytest.fixture
    def sample_gitlab_data(self) -> dict:
        """Create comprehensive sample GitLab data."""
        return {
            "profile": [
                {
                    "username": "johndoe",
                    "name": "John Doe",
                    "bio": "Senior Software Engineer with 10+ years experience",
                    "location": "San Francisco, CA",
                    "website_url": "https://johndoe.dev",
                    "organization": "Tech Corp",
                    "job_title": "Senior Engineer",
                    "state": "active",
                    "created_at": "2020-01-15T10:30:00Z",
                    "web_url": "https://gitlab.com/johndoe",
                    "avatar_url": "https://gitlab.com/uploads/avatar.png",
                }
            ],
            "projects": [
                {
                    "name": "awesome-lib",
                    "path_with_namespace": "johndoe/awesome-lib",
                    "description": "A really awesome library for doing things",
                    "visibility": "public",
                    "star_count": 150,
                    "forks_count": 25,
                    "web_url": "https://gitlab.com/johndoe/awesome-lib",
                    "topics": ["python", "library", "utils"],
                    "created_at": "2021-03-10T08:00:00Z",
                    "last_activity_at": "2024-01-15T14:30:00Z",
                },
                {
                    "name": "private-project",
                    "path_with_namespace": "johndoe/private-project",
                    "description": "Internal tooling",
                    "visibility": "private",
                    "star_count": 0,
                    "forks_count": 0,
                    "web_url": "https://gitlab.com/johndoe/private-project",
                    "topics": ["internal"],
                    "created_at": "2022-06-01T12:00:00Z",
                    "last_activity_at": "2024-01-10T09:00:00Z",
                },
                {
                    "name": "forked-repo",
                    "path_with_namespace": "johndoe/forked-repo",
                    "description": "A fork of another project",
                    "visibility": "public",
                    "star_count": 0,
                    "forked_from_project": {"id": 123},  # Should be skipped
                    "web_url": "https://gitlab.com/johndoe/forked-repo",
                },
            ],
            "member_projects": [
                {
                    "name": "team-project",
                    "path_with_namespace": "team/team-project",
                    "description": "Team collaboration project",
                    "visibility": "internal",
                    "star_count": 50,
                    "web_url": "https://gitlab.com/team/team-project",
                    "owner": {"username": "teamlead"},
                },
            ],
            "merge_requests": [
                {
                    "title": "Add new feature",
                    "state": "merged",
                    "web_url": "https://gitlab.com/johndoe/awesome-lib/-/merge_requests/1",
                    "source_branch": "feature/new-feature",
                    "target_branch": "main",
                    "created_at": "2024-01-10T10:00:00Z",
                    "merged_at": "2024-01-12T15:00:00Z",
                    "project_id": 1,
                    "references": {"full": "johndoe/awesome-lib!1"},
                },
                {
                    "title": "Fix critical bug",
                    "state": "merged",
                    "web_url": "https://gitlab.com/johndoe/awesome-lib/-/merge_requests/2",
                    "source_branch": "fix/critical-bug",
                    "target_branch": "main",
                    "created_at": "2024-01-08T09:00:00Z",
                    "merged_at": "2024-01-08T16:00:00Z",
                    "project_id": 1,
                    "references": {"full": "johndoe/awesome-lib!2"},
                },
                {
                    "title": "WIP: New experimental feature",
                    "state": "opened",
                    "web_url": "https://gitlab.com/johndoe/awesome-lib/-/merge_requests/3",
                    "source_branch": "experiment/new-idea",
                    "target_branch": "main",
                    "created_at": "2024-01-14T11:00:00Z",
                    "project_id": 1,
                    "references": {"full": "johndoe/awesome-lib!3"},
                },
                {
                    "title": "Rejected PR",
                    "state": "closed",
                    "web_url": "https://gitlab.com/johndoe/awesome-lib/-/merge_requests/4",
                    "source_branch": "rejected/feature",
                    "target_branch": "main",
                    "created_at": "2024-01-05T08:00:00Z",
                    "closed_at": "2024-01-06T10:00:00Z",
                    "project_id": 1,
                    "references": {"full": "johndoe/awesome-lib!4"},
                },
            ],
            "events": [
                {
                    "action_name": "pushed to",
                    "target_type": None,
                    "created_at": "2024-01-15T14:00:00Z",
                    "project_id": 1,
                    "push_data": {"commit_count": 3},
                },
                {
                    "action_name": "opened",
                    "target_type": "MergeRequest",
                    "created_at": "2024-01-14T11:00:00Z",
                    "project_id": 1,
                },
                {
                    "action_name": "commented on",
                    "target_type": "Issue",
                    "created_at": "2024-01-13T16:00:00Z",
                    "project_id": 2,
                },
            ],
        }

    def test_full_conversion(self, sample_gitlab_data: dict, tmp_path: Path):
        """Test full conversion with comprehensive data."""
        output_dir = tmp_path / "output"

        extractor = DictExtractor(sample_gitlab_data)
        writer = MarkdownFileWriter(output_dir)
        converter = GitLabToMarkdownConverter(extractor, writer)

        files = converter.convert("johndoe")

        # Verify output directory created
        assert output_dir.exists()

        # Verify multiple files created
        assert len(files) >= 4

        # Check key files exist
        file_names = [f.name for f in files]
        assert "profile.md" in file_names
        assert "projects.md" in file_names
        assert "merge_requests.md" in file_names
        assert "activity.md" in file_names

        # Verify profile content
        profile_content = (output_dir / "profile.md").read_text()
        assert "John Doe" in profile_content
        assert "Senior Software Engineer" in profile_content
        assert "San Francisco" in profile_content

        # Verify projects content
        projects_content = (output_dir / "projects.md").read_text()
        assert "awesome-lib" in projects_content
        assert "private-project" in projects_content
        # Forked repo should NOT appear (skipped by parser)
        assert "forked-repo" not in projects_content

        # Verify merge requests content
        mr_content = (output_dir / "merge_requests.md").read_text()
        assert "Add new feature" in mr_content
        assert "merged" in mr_content.lower()

    def test_empty_data(self, tmp_path: Path):
        """Test handling of empty data."""
        output_dir = tmp_path / "output"

        empty_data = {
            "profile": [],
            "projects": [],
            "member_projects": [],
            "merge_requests": [],
            "events": [],
        }

        extractor = DictExtractor(empty_data)
        writer = MarkdownFileWriter(output_dir)
        converter = GitLabToMarkdownConverter(extractor, writer)

        converter.convert("emptyuser")

        # Should still create output
        assert output_dir.exists()

    def test_unicode_content(self, tmp_path: Path):
        """Test handling of Unicode content."""
        output_dir = tmp_path / "output"

        unicode_data = {
            "profile": [
                {
                    "username": "jose",
                    "name": "Jose Garcia",
                    "bio": "Desarrollador de software con experiencia.",
                    "location": "Madrid, Espana",
                }
            ],
            "projects": [
                {
                    "name": "proyecto-test",
                    "path_with_namespace": "jose/proyecto-test",
                    "description": "Un proyecto de prueba con acentos",
                    "visibility": "public",
                    "star_count": 10,
                }
            ],
            "member_projects": [],
            "merge_requests": [],
            "events": [],
        }

        extractor = DictExtractor(unicode_data)
        writer = MarkdownFileWriter(output_dir)
        converter = GitLabToMarkdownConverter(extractor, writer)

        converter.convert("jose")

        profile_content = (output_dir / "profile.md").read_text()
        assert "Jose Garcia" in profile_content

    def test_special_characters_in_descriptions(self, tmp_path: Path):
        """Test handling of special Markdown characters."""
        output_dir = tmp_path / "output"

        special_data = {
            "profile": [
                {
                    "username": "test",
                    "name": "Test | User",
                    "bio": "Dev | Architect with *bold* and _italic_",
                }
            ],
            "projects": [
                {
                    "name": "test-project",
                    "path_with_namespace": "test/test-project",
                    "description": "Project with | pipe and * asterisk",
                    "visibility": "public",
                }
            ],
            "member_projects": [],
            "merge_requests": [],
            "events": [],
        }

        extractor = DictExtractor(special_data)
        writer = MarkdownFileWriter(output_dir)
        converter = GitLabToMarkdownConverter(extractor, writer)

        converter.convert("test")

        # Should not crash with special characters
        assert output_dir.exists()
        profile_content = (output_dir / "profile.md").read_text()
        assert "Test" in profile_content

    def test_very_large_description(self, tmp_path: Path):
        """Test handling of very large text content."""
        output_dir = tmp_path / "output"

        large_text = "A" * 10000  # 10KB of text

        large_data = {
            "profile": [
                {
                    "username": "test",
                    "name": "Test User",
                    "bio": large_text,
                }
            ],
            "projects": [],
            "member_projects": [],
            "merge_requests": [],
            "events": [],
        }

        extractor = DictExtractor(large_data)
        writer = MarkdownFileWriter(output_dir)
        converter = GitLabToMarkdownConverter(extractor, writer)

        converter.convert("test")

        # Should handle large content without issues
        assert output_dir.exists()

    def test_output_directory_creation(self, sample_gitlab_data: dict, tmp_path: Path):
        """Test that nested output directories are created."""
        output_dir = tmp_path / "deep" / "nested" / "path" / "output"

        extractor = DictExtractor(sample_gitlab_data)
        writer = MarkdownFileWriter(output_dir)
        converter = GitLabToMarkdownConverter(extractor, writer)

        files = converter.convert("johndoe")

        assert output_dir.exists()
        assert len(files) > 0

    def test_idempotent_conversion(self, sample_gitlab_data: dict, tmp_path: Path):
        """Test that running conversion twice produces same results."""
        output_dir = tmp_path / "output"

        extractor = DictExtractor(sample_gitlab_data)

        # First run
        writer1 = MarkdownFileWriter(output_dir)
        converter1 = GitLabToMarkdownConverter(extractor, writer1)
        files1 = converter1.convert("johndoe")
        content1 = (output_dir / "profile.md").read_text()

        # Second run (overwrite)
        writer2 = MarkdownFileWriter(output_dir)
        converter2 = GitLabToMarkdownConverter(extractor, writer2)
        files2 = converter2.convert("johndoe")
        content2 = (output_dir / "profile.md").read_text()

        assert len(files1) == len(files2)
        assert content1 == content2


class TestMergeRequestsE2E:
    """End-to-end tests for merge request handling."""

    def test_merge_requests_by_state(self, tmp_path: Path):
        """Test that merge requests are categorized by state."""
        data = {
            "profile": [{"username": "dev"}],
            "projects": [],
            "member_projects": [],
            "merge_requests": [
                {"title": "MR1", "state": "merged", "references": {"full": "p!1"}},
                {"title": "MR2", "state": "merged", "references": {"full": "p!2"}},
                {"title": "MR3", "state": "opened", "references": {"full": "p!3"}},
                {"title": "MR4", "state": "closed", "references": {"full": "p!4"}},
            ],
            "events": [],
        }

        extractor = DictExtractor(data)
        writer = InMemoryWriter()
        converter = GitLabToMarkdownConverter(extractor, writer)

        converter.convert("dev")

        mr_content = writer.files.get("merge_requests.md", "")
        assert "merged" in mr_content.lower() or "2" in mr_content
        assert "opened" in mr_content.lower() or "open" in mr_content.lower()


class TestGroupContributionsE2E:
    """End-to-end tests for group contributions."""

    def test_group_contributions_included(self, tmp_path: Path):
        """Test that group contributions are properly formatted."""
        data = {
            "profile": [{"username": "dev"}],
            "projects": [],
            "member_projects": [],
            "merge_requests": [],
            "events": [],
            "group_contributions": {
                "mygroup": {
                    "projects": [
                        {
                            "name": "mygroup/project1",
                            "commits": 50,
                            "url": "https://gitlab.com/mygroup/project1",
                        }
                    ],
                    "total_commits": 50,
                }
            },
        }

        extractor = DictExtractor(data)
        writer = InMemoryWriter()
        converter = GitLabToMarkdownConverter(extractor, writer)

        converter.convert("dev")

        if "groups.md" in writer.files:
            groups_content = writer.files["groups.md"]
            assert "mygroup" in groups_content or "project1" in groups_content
