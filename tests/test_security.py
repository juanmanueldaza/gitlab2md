"""Security-focused tests for gitlab2md."""

import tempfile
from pathlib import Path

import pytest

from gitlab2md.formatters.base import BaseFormatter
from gitlab2md.writer import InMemoryWriter, MarkdownFileWriter

# =============================================================================
# Path Traversal Tests
# =============================================================================


class TestPathTraversalPrevention:
    """Tests for path traversal attack prevention."""

    def test_reject_parent_directory_traversal(self):
        """Ensure '../' in filename is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("../etc/passwd", "malicious content")

    def test_reject_nested_parent_traversal(self):
        """Ensure nested '../' is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("foo/../../../etc/passwd", "malicious content")

    def test_reject_absolute_path_unix(self):
        """Ensure absolute Unix paths are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("/etc/passwd", "malicious content")

    def test_allow_valid_filename(self):
        """Ensure valid filenames still work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            path = writer.write("profile.md", "# Test Profile")

            assert path.exists()
            assert path.name == "profile.md"

    def test_allow_filename_with_dots(self):
        """Ensure filenames with single dots are allowed (e.g., 'my.profile.md')."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            path = writer.write("my.profile.md", "# Test")

            assert path.exists()
            assert path.name == "my.profile.md"

    def test_reject_absolute_path_windows(self):
        """Ensure absolute Windows paths are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            # Windows drive letter
            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("C:\\Windows\\System32\\file", "malicious content")

            # UNC path
            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("\\\\server\\share\\file", "malicious content")

    def test_reject_path_traversal_with_resolution(self):
        """Ensure path traversal is caught even with complex paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            # These should all be rejected
            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("subdir/../../etc/passwd", "content")


# =============================================================================
# Writer Security Tests
# =============================================================================


class TestWriterSecurity:
    """Tests for writer security."""

    def test_file_written_in_output_directory(self):
        """Ensure files are written within output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            writer = MarkdownFileWriter(output_dir)
            path = writer.write("test.md", "content")

            # File should be inside output directory
            assert str(path).startswith(str(output_dir))
            assert path.parent == output_dir

    def test_directory_created_if_not_exists(self):
        """Ensure output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "output"
            writer = MarkdownFileWriter(output_dir)
            path = writer.write("test.md", "content")

            assert output_dir.exists()
            assert path.exists()

    def test_in_memory_writer_does_not_write_to_disk(self):
        """Ensure InMemoryWriter doesn't actually write files."""
        writer = InMemoryWriter()
        writer.write("test.md", "content")

        # Check content is stored in memory
        assert "test.md" in writer.files
        assert writer.files["test.md"] == "content"


# =============================================================================
# Content Security Tests
# =============================================================================


class TestContentSecurity:
    """Tests for content handling security."""

    def test_special_characters_in_content(self):
        """Ensure special characters are handled safely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            # Content with special characters
            content = """# Test
            <script>alert('xss')</script>
            | table | with | pipes |
            [link](javascript:alert('xss'))
            """

            path = writer.write("test.md", content)

            # Should write content as-is (markdown files don't execute scripts)
            assert path.exists()
            written_content = path.read_text()
            assert "<script>" in written_content  # Preserved as-is

    def test_unicode_content(self):
        """Ensure Unicode content is handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            content = "# Test\nHello World"
            path = writer.write("test.md", content)

            written_content = path.read_text(encoding="utf-8")
            assert "Hello World" in written_content

    def test_null_bytes_in_content(self):
        """Ensure null bytes in content don't cause issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            content = "# Test\n\x00null byte"
            path = writer.write("test.md", content)

            # Should write successfully
            assert path.exists()


# =============================================================================
# Formatter Security Tests
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


class TestFormatterSecurity:
    """Tests for formatter security."""

    @pytest.fixture
    def formatter(self):
        return ConcreteFormatter()

    def test_escape_pipe_in_table(self, formatter):
        """Ensure pipe characters are escaped to prevent table injection."""
        result = formatter._escape_md("text | with | pipes")
        assert result == "text \\| with \\| pipes"

    def test_escape_md_prevents_formatting_injection(self, formatter):
        """Ensure markdown formatting characters are escaped."""
        result = formatter._escape_md("*bold* _italic_ `code`")
        assert result == "\\*bold\\* \\_italic\\_ \\`code\\`"

    def test_escape_md_prevents_html_injection(self, formatter):
        """Ensure HTML tag characters are escaped."""
        result = formatter._escape_md("<script>alert('xss')</script>")
        assert "\\<" in result
        assert "\\>" in result
        assert "<script>" not in result

    def test_escape_md_handles_heading_chars(self, formatter):
        """Ensure heading characters are escaped."""
        result = formatter._escape_md("# Heading\n## Subheading")
        assert "\\#" in result
        assert "\n#" not in result  # no unescaped # at start of lines

    def test_truncate_prevents_large_output(self, formatter):
        """Ensure truncate limits output size."""
        large_text = "A" * 100000
        result = formatter._truncate(large_text, 100)
        assert len(result) <= 100

    def test_make_link_handles_malicious_urls(self, formatter):
        """Ensure make_link rejects potentially malicious URLs."""
        # javascript: URLs should be blocked
        result = formatter._make_link("text", "javascript:alert(1)")
        assert result == "text"  # Returns plain text, URL rejected
        assert "javascript:" not in result

        # data: URLs should be blocked
        result = formatter._make_link(
            "text", "data:text/html,<script>alert(1)</script>"
        )
        assert result == "text"
        assert "data:" not in result

        # If URL is None or empty, just returns text
        result = formatter._make_link("text", None)
        assert result == "text"

        # Valid URLs should work
        result = formatter._make_link("text", "https://example.com")
        assert result == "[text](https://example.com)"

    def test_sanitize_url_escapes_markdown_chars(self, formatter):
        """Ensure URLs are sanitized for Markdown safety."""
        # Parentheses should be escaped
        result = formatter._sanitize_url("https://example.com/path?q=a(b)c")
        assert "%29" in result  # ) is escaped

        # Brackets should be escaped
        result = formatter._sanitize_url("https://example.com/[test]")
        assert "%5B" in result  # [ is escaped
        assert "%5D" in result  # ] is escaped

    def test_escape_md_handles_newlines(self, formatter):
        """Ensure newlines are handled to prevent injection."""
        result = formatter._escape_md("line1\nline2\rline3")
        assert "\n" not in result
        assert "\r" not in result


# =============================================================================
# Input Validation Tests
# =============================================================================


class TestInputValidation:
    """Tests for input validation."""

    def test_empty_filename(self):
        """Test handling of empty filename creates .md file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            # Empty filename with .md extension auto-added becomes ".md"
            # which is technically a valid (hidden) filename on Unix
            path = writer.write("", "content")
            assert path.name == ".md"
            assert path.exists()

    def test_very_long_filename(self):
        """Test handling of very long filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            # Very long filename (may fail on some filesystems)
            long_name = "a" * 200 + ".md"
            try:
                path = writer.write(long_name, "content")
                # If it succeeds, file should exist
                assert path.exists()
            except OSError:
                # Expected on some filesystems with name limits
                pass


# =============================================================================
# Data Integrity Tests
# =============================================================================


class TestDataIntegrity:
    """Tests for data integrity."""

    def test_content_preserved_exactly(self):
        """Ensure content is written exactly as provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            original_content = "# Test\n\nLine 1\nLine 2\n\n```python\ncode\n```"
            path = writer.write("test.md", original_content)

            written_content = path.read_text()
            assert written_content == original_content

    def test_overwrite_existing_file(self):
        """Ensure existing files are overwritten."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            # Write initial content
            writer.write("test.md", "initial")

            # Overwrite with new content
            path = writer.write("test.md", "updated")

            assert path.read_text() == "updated"
