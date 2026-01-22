"""Output writers for markdown files."""

from pathlib import Path

from gitlab2md.protocols import OutputWriter


class MarkdownFileWriter(OutputWriter):
    """Write markdown content to files.

    Single Responsibility: Only handles file I/O with security validation.
    """

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def _validate_filename(self, filename: str) -> None:
        """Validate filename to prevent path traversal and injection attacks.

        Raises:
            ValueError: If filename contains path traversal or invalid chars.
        """
        # Check for null bytes (can truncate filenames on some systems)
        if "\x00" in filename:
            raise ValueError("Invalid filename: contains null byte")

        # Check for parent directory traversal
        if ".." in filename:
            raise ValueError(f"Invalid filename: {filename}")

        # Check for absolute Unix paths
        if filename.startswith("/"):
            raise ValueError(f"Invalid filename: {filename}")

        # Check for absolute Windows paths (e.g., C:\, \\server, \\?\)
        if filename.startswith("\\") or (len(filename) > 1 and filename[1] == ":"):
            raise ValueError(f"Invalid filename: {filename}")

        # Ensure resolved path stays within output directory (canonical check)
        test_path = (self._output_dir / filename).resolve()
        output_resolved = self._output_dir.resolve()
        if not str(test_path).startswith(str(output_resolved)):
            raise ValueError(f"Invalid filename: {filename}")

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
        self._validate_filename(filename)

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
