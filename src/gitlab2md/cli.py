"""Command-line interface for gitlab2md."""

import argparse
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

    args = parser.parse_args()

    # Determine username
    username = args.username
    if not username:
        username = get_authenticated_user()
        if not username:
            print(
                "Error: No username provided and not authenticated with glab CLI.",
                file=sys.stderr,
            )
            print(
                "Either provide a username or run 'glab auth login' first.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Using authenticated user: {username}")

    # Validate username using shared validation
    try:
        validate_gitlab_name(username, "username")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Check glab CLI is available
    try:
        subprocess.run(["glab", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        print(
            "Error: glab CLI not found. Install from https://gitlab.com/gitlab-org/cli",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse and validate groups using shared validation
    groups = None
    if args.groups:
        groups = [g.strip() for g in args.groups.split(",") if g.strip()]
        try:
            for group in groups:
                validate_gitlab_name(group, "group")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Run conversion
    try:
        converter = create_converter(args.output, groups=groups)
        print(f"Fetching GitLab data for: {username}")
        if groups:
            print(f"Including group contributions: {', '.join(groups)}")
        files = converter.convert(username)

        print(f"\nCreated {len(files)} files in {args.output}/")
        for f in files:
            print(f"  - {f.name}")

    except ValueError as e:
        # Validation errors
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        # API/CLI errors (already sanitized)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        # Unexpected errors - don't expose details
        print("Error: An unexpected error occurred.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
