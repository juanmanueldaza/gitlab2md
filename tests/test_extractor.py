"""Tests for GitLabExtractor error handling and logging."""

import logging

import pytest

from gitlab2md.extractor import GitLabExtractor


class TestSafeExtractLogging:
    """Ensure swallowed extraction errors are logged, not silenced.

    Regression coverage for the silent ``except Exception`` blocks that
    previously hid all failures (OWASP A09:2021 - Security Logging and
    Monitoring Failures).
    """

    def test_safe_extract_list_logs_warning_on_error(self, monkeypatch, caplog):
        """A failing list extraction returns [] but emits a warning."""
        extractor = GitLabExtractor()

        def boom(*args):
            raise RuntimeError("glab exploded")

        monkeypatch.setattr(extractor, "_run_glab_json", boom)

        with caplog.at_level(logging.WARNING):
            result = extractor._safe_extract_list("api", "/users?username=test")

        assert result == []
        assert any(record.levelno == logging.WARNING for record in caplog.records)
        assert "glab exploded" in caplog.text

    def test_safe_extract_dict_logs_warning_on_error(self, monkeypatch, caplog):
        """A failing dict extraction returns {} but emits a warning."""
        extractor = GitLabExtractor()

        def boom(*args):
            raise RuntimeError("glab exploded")

        monkeypatch.setattr(extractor, "_run_glab_json", boom)

        with caplog.at_level(logging.WARNING):
            result = extractor._safe_extract_dict("api", "/some/endpoint")

        assert result == {}
        assert "glab exploded" in caplog.text

    @pytest.mark.parametrize(
        "method_name",
        ["_get_snippets", "_get_ssh_keys", "_get_gpg_keys", "_get_memberships"],
    )
    def test_profile_dependent_getters_log_on_error(
        self, method_name, monkeypatch, caplog
    ):
        """Profile-dependent getters log and return [] when extraction fails."""
        extractor = GitLabExtractor()

        def boom(*args):
            raise RuntimeError("network down")

        # Force the underlying call to raise inside the method's try block.
        monkeypatch.setattr(extractor, "_safe_extract_list", boom)

        method = getattr(extractor, method_name)
        with caplog.at_level(logging.WARNING):
            result = method("test-user")

        assert result == []
        assert any(record.levelno == logging.WARNING for record in caplog.records)
