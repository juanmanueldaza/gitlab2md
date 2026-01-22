"""gitlab2md - Convert GitLab profile data to Markdown for LLM analysis."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gitlab2md")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Development/editable install

from .converter import GitLabToMarkdownConverter, create_converter

__all__ = ["GitLabToMarkdownConverter", "create_converter", "__version__"]
