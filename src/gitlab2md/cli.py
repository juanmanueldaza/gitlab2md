"""Command-line interface for gitlab2md."""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from . import __version__
from .converter import create_converter
from .validation import validate_gitlab_name


def get_authenticated_user() -> str | None:
    """Get the currently authenticated GitLab user via glab CLI.

    Returns:
        Username string or None if not authenticated.
    """
    try:
        result = subprocess.run(
            ["glab", "api", "/user", "--jq", ".username"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="gitlab2md",
        description="Convert GitLab profile data to Markdown for LLM analysis",
    )
    parser.add_argument(
        "username",
        nargs="?",
        help="GitLab username to fetch data for (defaults to authenticated user)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("gitlab_export"),
        help="Output directory for Markdown files (default: gitlab_export)",
    )
    parser.add_argument(
        "--groups",
        help="Comma-separated list of groups to check for contributions",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output",
    )

    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARNING
    logging.basicConfig(level=log_level, format="%(message)s")

    # Determine username
    username = args.username
    if not username:
        username = get_authenticated_user()
        if not username:
            logging.error("No username provided and not authenticated with glab CLI.")
            logging.error("Either provide a username or run 'glab auth login' first.")
            sys.exit(1)
        logging.info("Using authenticated user: %s", username)

    # Validate username using shared validation
    try:
        validate_gitlab_name(username, "username")
    except ValueError as e:
        logging.error("Error: %s", e)
        sys.exit(1)

    # Check glab CLI is available
    try:
        subprocess.run(["glab", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        logging.error("glab CLI not found. Install from https://gitlab.com/gitlab-org/cli")
        sys.exit(1)

    # Parse and validate groups using shared validation
    groups = None
    if args.groups:
        groups = [g.strip() for g in args.groups.split(",") if g.strip()]
        try:
            for group in groups:
                validate_gitlab_name(group, "group")
        except ValueError as e:
            logging.error("Error: %s", e)
            sys.exit(1)

    # Run conversion
    try:
        converter = create_converter(args.output, groups=groups)
        logging.info("Fetching GitLab data for: %s", username)
        if groups:
            logging.info("Including group contributions: %s", ", ".join(groups))
        files = converter.convert(username)

        logging.info("\nCreated %d files in %s/", len(files), args.output)
        for f in files:
            logging.info("  - %s", f.name)

    except ValueError as e:
        logging.error("Error: %s", e)
        sys.exit(1)
    except RuntimeError as e:
        logging.error("Error: %s", e)
        sys.exit(1)
    except Exception:
        logging.error("Error: An unexpected error occurred.")
        sys.exit(1)


if __name__ == "__main__":
    main()
