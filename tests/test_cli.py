"""Tests for CLI module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gitlab2md.cli import get_authenticated_user, main


class TestGetAuthenticatedUser:
    """Tests for getting authenticated user."""

    def test_returns_username_on_success(self):
        """Test successful username retrieval."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="testuser\n",
                returncode=0,
            )
            result = get_authenticated_user()
            assert result == "testuser"

    def test_returns_none_on_failure(self):
        """Test returns None when glab command fails."""
        with patch("subprocess.run") as mock_run:
            from subprocess import CalledProcessError

            mock_run.side_effect = CalledProcessError(1, "glab")
            result = get_authenticated_user()
            assert result is None

    def test_returns_none_when_glab_not_found(self):
        """Test returns None when glab CLI is not installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = get_authenticated_user()
            assert result is None


class TestMain:
    """Tests for main entry point."""

    def test_glab_not_found(self, capsys):
        """Test error when glab CLI is not found."""
        with patch("sys.argv", ["gitlab2md", "testuser"]):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError()
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "glab CLI not found" in captured.err

    def test_no_username_and_not_authenticated(self, capsys):
        """Test error when no username provided and not authenticated."""
        with patch("sys.argv", ["gitlab2md"]):
            with patch("gitlab2md.cli.get_authenticated_user", return_value=None):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "No username provided" in captured.err

    def test_successful_conversion(self, capsys, tmp_path):
        """Test successful conversion with mock extractor."""
        output_dir = tmp_path / "output"

        with patch("sys.argv", ["gitlab2md", "testuser", "-o", str(output_dir)]):
            # Mock glab version check
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                # Mock the converter
                with patch("gitlab2md.cli.create_converter") as mock_create:
                    mock_converter = MagicMock()
                    mock_converter.convert.return_value = [
                        Path("profile.md"),
                        Path("projects.md"),
                    ]
                    mock_create.return_value = mock_converter

                    main()

        captured = capsys.readouterr()
        assert "Created 2 files" in captured.out

    def test_uses_authenticated_user_when_no_username(self, capsys, tmp_path):
        """Test that authenticated user is used when no username provided."""
        output_dir = tmp_path / "output"

        with patch("sys.argv", ["gitlab2md", "-o", str(output_dir)]):
            with patch("gitlab2md.cli.get_authenticated_user", return_value="authuser"):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)

                    with patch("gitlab2md.cli.create_converter") as mock_create:
                        mock_converter = MagicMock()
                        mock_converter.convert.return_value = [Path("profile.md")]
                        mock_create.return_value = mock_converter

                        main()

        captured = capsys.readouterr()
        assert "authuser" in captured.out

    def test_groups_option(self, capsys, tmp_path):
        """Test --groups option is parsed correctly."""
        output_dir = tmp_path / "output"

        with patch(
            "sys.argv",
            [
                "gitlab2md",
                "testuser",
                "-o",
                str(output_dir),
                "--groups",
                "group1,group2",
            ],
        ):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                with patch("gitlab2md.cli.create_converter") as mock_create:
                    mock_converter = MagicMock()
                    mock_converter.convert.return_value = [Path("profile.md")]
                    mock_create.return_value = mock_converter

                    main()

                    # Check that groups were passed
                    call_args = mock_create.call_args
                    assert call_args[1]["groups"] == ["group1", "group2"]

        captured = capsys.readouterr()
        assert "group1" in captured.out or "group2" in captured.out

    def test_conversion_error(self, capsys, tmp_path):
        """Test handling of conversion errors."""
        output_dir = tmp_path / "output"

        with patch("sys.argv", ["gitlab2md", "testuser", "-o", str(output_dir)]):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                with patch("gitlab2md.cli.create_converter") as mock_create:
                    mock_converter = MagicMock()
                    mock_converter.convert.side_effect = RuntimeError("API error")
                    mock_create.return_value = mock_converter

                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error" in captured.err


class TestArgumentParsing:
    """Tests for argument parsing."""

    def test_default_output_directory(self, capsys, tmp_path):
        """Test default output directory is 'gitlab_export'."""
        with patch("sys.argv", ["gitlab2md", "testuser"]):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                with patch("gitlab2md.cli.create_converter") as mock_create:
                    mock_converter = MagicMock()
                    mock_converter.convert.return_value = [Path("profile.md")]
                    mock_create.return_value = mock_converter

                    main()

                    call_args = mock_create.call_args
                    assert call_args[0][0] == Path("gitlab_export")

    def test_custom_output_directory(self, capsys, tmp_path):
        """Test custom output directory is used."""
        custom_output = tmp_path / "custom_output"

        with patch("sys.argv", ["gitlab2md", "testuser", "-o", str(custom_output)]):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                with patch("gitlab2md.cli.create_converter") as mock_create:
                    mock_converter = MagicMock()
                    mock_converter.convert.return_value = [Path("profile.md")]
                    mock_create.return_value = mock_converter

                    main()

                    call_args = mock_create.call_args
                    assert call_args[0][0] == custom_output
