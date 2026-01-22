"""Abstract interfaces following SOLID principles.

This module defines Protocol classes that serve as contracts for the system.
All implementations depend on these abstractions, not concrete classes
(Dependency Inversion Principle).
"""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DataExtractor(Protocol):
    """Protocol for extracting raw data from GitLab API.

    Implementations:
    - GitLabExtractor: Real extraction via glab CLI
    - DictExtractor: Mock for testing
    """

    def extract(self, username: str) -> dict[str, Any]:
        """Extract all data for a GitLab user.

        Args:
            username: GitLab username to extract data for.

        Returns:
            Dictionary with all extracted data sections.
        """
        ...


@runtime_checkable
class SectionParser(Protocol):
    """Protocol for parsing one section of raw GitLab data.

    Each parser handles ONE section (Single Responsibility Principle).
    New parsers can be added via @register_parser decorator
    (Open/Closed Principle).
    """

    @property
    def section_key(self) -> str:
        """Unique identifier for this section (e.g., 'profile', 'projects')."""
        ...

    def parse(self, raw_data: dict[str, Any]) -> Any:
        """Parse raw data into structured format.

        Args:
            raw_data: Raw data dictionary from extractor.

        Returns:
            Parsed data in section-specific format.
        """
        ...


@runtime_checkable
class SectionFormatter(Protocol):
    """Protocol for formatting parsed data into Markdown.

    Each formatter handles ONE section (Single Responsibility Principle).
    New formatters can be added via @register_formatter decorator
    (Open/Closed Principle).
    """

    @property
    def section_key(self) -> str:
        """Unique identifier for this section (must match parser)."""
        ...

    @property
    def output_filename(self) -> str:
        """Output filename for this section (e.g., 'profile.md')."""
        ...

    def format(self, parsed_data: Any) -> str:
        """Format parsed data into Markdown string.

        Args:
            parsed_data: Parsed data from corresponding parser.

        Returns:
            Markdown formatted string.
        """
        ...


@runtime_checkable
class OutputWriter(Protocol):
    """Protocol for writing content to output destination.

    Implementations:
    - MarkdownFileWriter: Write to filesystem with security validation
    - InMemoryWriter: Write to memory for testing
    """

    def write(self, filename: str, content: str) -> Path:
        """Write content to destination and return path.

        Args:
            filename: The filename to write to.
            content: The content to write.

        Returns:
            Path to the written file.

        Raises:
            ValueError: If filename is invalid (e.g., path traversal).
        """
        ...


@runtime_checkable
class ParserRegistry(Protocol):
    """Protocol for parser registry."""

    def register(self, parser: SectionParser) -> None:
        """Register a section parser."""
        ...

    def get_all(self) -> list[SectionParser]:
        """Get all registered parsers."""
        ...


@runtime_checkable
class FormatterRegistry(Protocol):
    """Protocol for formatter registry."""

    def register(self, formatter: SectionFormatter) -> None:
        """Register a section formatter."""
        ...

    def get_all(self) -> list[SectionFormatter]:
        """Get all registered formatters."""
        ...
