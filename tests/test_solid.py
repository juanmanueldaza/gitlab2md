"""Tests for SOLID-compliant architecture."""

import tempfile
from pathlib import Path

from gitlab2md.converter import GitLabToMarkdownConverter, create_converter
from gitlab2md.extractor import DictExtractor, GitLabExtractor
from gitlab2md.protocols import (
    DataExtractor,
    OutputWriter,
)
from gitlab2md.registry import (
    DefaultFormatterRegistry,
    DefaultParserRegistry,
    get_formatter_registry,
    get_parser_registry,
)
from gitlab2md.writer import InMemoryWriter, MarkdownFileWriter

# =============================================================================
# Protocol Tests
# =============================================================================


class TestDataExtractorProtocol:
    """Tests for DataExtractor protocol compliance."""

    def test_gitlab_extractor_implements_protocol(self):
        extractor = GitLabExtractor()
        assert isinstance(extractor, DataExtractor)

    def test_dict_extractor_implements_protocol(self):
        extractor = DictExtractor({})
        assert isinstance(extractor, DataExtractor)


class TestOutputWriterProtocol:
    """Tests for OutputWriter protocol compliance."""

    def test_markdown_file_writer_implements_protocol(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            assert isinstance(writer, OutputWriter)

    def test_in_memory_writer_implements_protocol(self):
        writer = InMemoryWriter()
        assert isinstance(writer, OutputWriter)


# =============================================================================
# Extractor Tests
# =============================================================================


class TestDictExtractor:
    """Tests for dict data extractor (testing helper)."""

    def test_extract_returns_data(self):
        test_data = {"profile": [{"name": "Test"}]}
        extractor = DictExtractor(test_data)
        result = extractor.extract("testuser")

        assert result["profile"] == test_data["profile"]
        assert result["username"] == "testuser"

    def test_extract_empty_data(self):
        extractor = DictExtractor({})
        result = extractor.extract("testuser")

        assert result["username"] == "testuser"


# =============================================================================
# Writer Tests
# =============================================================================


class TestMarkdownFileWriter:
    """Tests for file writer."""

    def test_write_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            path = writer.write("test.md", "# Hello")

            assert path.exists()
            assert path.name == "test.md"
            assert path.read_text() == "# Hello"

    def test_write_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "path"
            writer = MarkdownFileWriter(output_dir)
            path = writer.write("test.md", "# Hello")

            assert output_dir.exists()
            assert path.exists()


class TestInMemoryWriter:
    """Tests for in-memory writer (testing helper)."""

    def test_write_stores_content(self):
        writer = InMemoryWriter()
        writer.write("test.md", "# Hello")

        assert "test.md" in writer.files
        assert writer.files["test.md"] == "# Hello"

    def test_write_multiple_files(self):
        writer = InMemoryWriter()
        writer.write("a.md", "Content A")
        writer.write("b.md", "Content B")

        assert len(writer.files) == 2
        assert writer.files["a.md"] == "Content A"
        assert writer.files["b.md"] == "Content B"


# =============================================================================
# Registry Tests
# =============================================================================


class TestParserRegistry:
    """Tests for parser registry."""

    def test_register_and_get_all(self):
        registry = DefaultParserRegistry()

        class MockParser:
            @property
            def section_key(self) -> str:
                return "test"

            def parse(self, raw_data: dict) -> list:
                return []

        parser = MockParser()
        registry.register(parser)

        assert parser in registry.get_all()

    def test_global_registry_has_parsers(self):
        registry = get_parser_registry()
        parsers = registry.get_all()

        # Should have all registered parsers
        keys = [p.section_key for p in parsers]
        assert "profile" in keys
        assert "projects" in keys


class TestFormatterRegistry:
    """Tests for formatter registry."""

    def test_register_and_get_all(self):
        registry = DefaultFormatterRegistry()

        class MockFormatter:
            @property
            def section_key(self) -> str:
                return "test"

            @property
            def output_filename(self) -> str:
                return "test.md"

            def format(self, parsed_data):
                return ""

        formatter = MockFormatter()
        registry.register(formatter)

        assert formatter in registry.get_all()

    def test_global_registry_has_formatters(self):
        registry = get_formatter_registry()
        formatters = registry.get_all()

        # Should have all registered formatters
        keys = [f.section_key for f in formatters]
        assert "profile" in keys
        assert "projects" in keys


# =============================================================================
# Integration Tests
# =============================================================================


class TestGitLabToMarkdownConverter:
    """Integration tests for the main converter."""

    def test_convert_minimal_data(self):
        # Setup test data
        raw_data = {
            "profile": [
                {"username": "testuser", "name": "Test User", "bio": "Developer"}
            ],
            "projects": [
                {
                    "name": "my-project",
                    "path_with_namespace": "testuser/my-project",
                    "description": "A test project",
                    "visibility": "public",
                    "star_count": 5,
                    "web_url": "https://gitlab.com/testuser/my-project",
                }
            ],
            "member_projects": [],
            "merge_requests": [],
            "events": [],
        }

        extractor = DictExtractor(raw_data)
        writer = InMemoryWriter()

        converter = GitLabToMarkdownConverter(extractor, writer)
        files = converter.convert("testuser")

        # Should create profile.md and projects.md at minimum
        assert len(files) >= 2
        assert "profile.md" in writer.files
        assert "projects.md" in writer.files
        assert "Test User" in writer.files["profile.md"]
        assert "my-project" in writer.files["projects.md"]

    def test_convert_empty_data(self):
        raw_data = {
            "profile": [],
            "projects": [],
            "member_projects": [],
            "merge_requests": [],
            "events": [],
        }

        extractor = DictExtractor(raw_data)
        writer = InMemoryWriter()

        converter = GitLabToMarkdownConverter(extractor, writer)
        files = converter.convert("testuser")

        # Should still create some files
        assert len(files) >= 1


class TestCreateConverter:
    """Tests for the factory function."""

    def test_create_converter_returns_converter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = create_converter(Path(tmpdir))
            assert isinstance(converter, GitLabToMarkdownConverter)

    def test_create_converter_with_groups(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = create_converter(Path(tmpdir), groups=["mygroup"])
            assert isinstance(converter, GitLabToMarkdownConverter)
