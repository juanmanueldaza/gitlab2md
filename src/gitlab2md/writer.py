"""Output writers for markdown files."""

from pathlib import Path

from gitlab2md.protocols import OutputWriter
from gitlab2md.validation import validate_filename


class MarkdownFileWriter(OutputWriter):
    """Write markdown content to files.

    Single Responsibility: Only handles file I/O with security validation.
    """

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, filename: str, content: str) -> Path:
        """Write content to a file and return the path.

        Args:
            filename: The filename to write to (must be safe).
            content: The content to write.

        Returns:
            The path to the written file.

        Raises:
            ValueError: If filename contains path traversal attempts.
        """
        validate_filename(filename)

        # Add .md extension if not present
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        filepath = self._output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath


class InMemoryWriter(OutputWriter):
    """In-memory writer for testing.

    Single Responsibility: Store output in memory.
    """

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def write(self, filename: str, content: str) -> Path:
        """Store content in memory."""
        # Add .md extension if not present
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        self.files[filename] = content
        return Path(filename)
