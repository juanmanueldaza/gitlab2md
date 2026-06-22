"""Tests for GitLabExtractor error handling, logging, and caching."""

import json
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


class TestProfileCaching:
    """Ensure the profile lookup is fetched once and reused (issue #9)."""

    def _patch_glab(self, extractor, calls):
        """Replace _run_glab with a recorder returning canned JSON."""

        def fake_run_glab(*args):
            endpoint = args[1] if len(args) > 1 else ""
            calls.append(endpoint)
            if endpoint.startswith("/users?username="):
                return json.dumps([{"id": 42, "name": "Test User"}])
            return json.dumps([])

        extractor._run_glab = fake_run_glab

    def test_profile_fetched_once_per_extract(self):
        """A full extract() hits /users?username= exactly once, not per-getter."""
        extractor = GitLabExtractor()
        calls: list[str] = []
        self._patch_glab(extractor, calls)

        extractor.extract("test-user")

        profile_calls = [c for c in calls if c.startswith("/users?username=")]
        assert len(profile_calls) == 1

    def test_cached_profile_returns_same_data(self):
        """Repeated _cached_profile calls reuse the cached response."""
        extractor = GitLabExtractor()
        calls: list[str] = []
        self._patch_glab(extractor, calls)

        first = extractor._cached_profile("test-user")
        second = extractor._cached_profile("test-user")

        assert first == [{"id": 42, "name": "Test User"}]
        assert second == first
        assert calls.count("/users?username=test-user") == 1
