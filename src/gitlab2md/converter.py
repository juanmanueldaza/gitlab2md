"""Main orchestrator for GitLab to Markdown conversion.

SOLID Principles applied:
- Single Responsibility: Only orchestrates the conversion process
- Open/Closed: New parsers/formatters added via registries without modification
- Dependency Inversion: Depends on protocols (DataExtractor, OutputWriter),
  not concrete implementations
"""

import sys
from pathlib import Path
from typing import Any

# Import parsers and formatters to trigger registration
from . import (
    formatters,  # noqa: F401
    parsers,  # noqa: F401
)
from .extractor import GitLabExtractor
from .protocols import DataExtractor, OutputWriter
from .registry import get_formatter_registry, get_parser_registry
from .writer import MarkdownFileWriter


class GitLabToMarkdownConverter:
    """Convert GitLab profile data to Markdown files.

    This is the main orchestrator that coordinates:
    1. Data extraction from GitLab API
    2. Parsing raw data into structured sections
    3. Formatting sections into Markdown
    4. Writing output files

    All dependencies are injected via constructor (Dependency Inversion).
    """

    def __init__(
        self,
        extractor: DataExtractor,
        writer: OutputWriter,
    ) -> None:
        """Initialize converter with injected dependencies.

        Args:
            extractor: Data extractor implementation (protocol type).
            writer: Output writer implementation (protocol type).
        """
        self._extractor = extractor
        self._writer = writer
        self._parser_registry = get_parser_registry()
        self._formatter_registry = get_formatter_registry()

    def convert(self, username: str) -> list[Path]:
        """Convert GitLab data for a user to Markdown files.

        Args:
            username: GitLab username to convert data for.

        Returns:
            List of paths to created files.
        """
        # Step 1: Extract raw data
        raw_data = self._extractor.extract(username)

        # Step 2: Parse all sections
        parsed = self._parse_all(raw_data)

        # Step 3: Format and write all sections
        return self._format_and_write_all(parsed)

    def _parse_all(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Parse all sections using registered parsers.

        Args:
            raw_data: Raw data from extractor.

        Returns:
            Dictionary mapping section_key to parsed data.
        """
        parsed: dict[str, Any] = {}

        for parser in self._parser_registry.get_all():
            try:
                parsed[parser.section_key] = parser.parse(raw_data)
            except Exception as e:
                # Log warning but continue with other sections
                print(
                    f"Warning: Parser '{parser.section_key}' failed: {e}",
                    file=sys.stderr,
                )
                parsed[parser.section_key] = None

        return parsed

    def _format_and_write_all(self, parsed: dict[str, Any]) -> list[Path]:
        """Format and write all sections using registered formatters.

        Args:
            parsed: Dictionary of parsed section data.

        Returns:
            List of paths to created files.
        """
        created_files: list[Path] = []

        for formatter in self._formatter_registry.get_all():
            section_data = parsed.get(formatter.section_key)
            if section_data is None:
                continue

            try:
                markdown = formatter.format(section_data)
                if markdown and markdown.strip():
                    path = self._writer.write(formatter.output_filename, markdown)
                    created_files.append(path)
            except Exception as e:
                # Log warning but continue with other sections
                print(
                    f"Warning: Formatter '{formatter.section_key}' failed: {e}",
                    file=sys.stderr,
                )

        return created_files


def create_converter(
    output_dir: Path,
    groups: list[str] | None = None,
) -> GitLabToMarkdownConverter:
    """Factory function to create a converter with default dependencies.

    This provides a convenient way to create a fully configured converter
    while still allowing dependency injection for testing.

    Args:
        output_dir: Directory to write output files to.
        groups: Optional list of groups to check for contributions.

    Returns:
        Configured GitLabToMarkdownConverter instance.
    """
    extractor = GitLabExtractor(groups=groups)
    writer = MarkdownFileWriter(output_dir)
    return GitLabToMarkdownConverter(extractor, writer)
