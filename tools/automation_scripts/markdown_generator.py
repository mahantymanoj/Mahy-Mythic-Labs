"""Create consistent Markdown documents without overwriting existing files."""

from __future__ import annotations

import argparse
from pathlib import Path


def create_markdown_document(path: Path, title: str) -> Path:
    """Create a starter Markdown document if it does not already exist."""
    if path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing file: {path}. "
            "Create a new filename or edit it manually."
        )

    path.parent.mkdir(parents=True, exist_ok=True)

    content = f"""# {title}

## Purpose

Describe the purpose of this document.

## Status

Draft

## Notes

- 
"""

    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Mahy Mythic Labs Markdown starter document."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("path", help="Destination Markdown file path")
    create_parser.add_argument("title", help="Document title")

    args = parser.parse_args()

    if args.command == "create":
        output_path = create_markdown_document(Path(args.path), args.title)
        print(f"Created Markdown document: {output_path}")


if __name__ == "__main__":
    main()