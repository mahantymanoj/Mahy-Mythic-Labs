"""Read-only MCP server for safe Mahy Mythic Labs project-file access."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Mahy Mythic Labs Filesystem",
    instructions=(
        "Read-only access to the Mahy Mythic Labs project. "
        "Never assume permission to modify, delete, move, or create files."
    ),
)

PROJECT_ROOT = Path(os.getenv("MAHY_PROJECT_ROOT", ".")).resolve()
MAX_FILE_BYTES = 200_000
MAX_RESULTS = 100


def resolve_project_path(relative_path: str) -> Path:
    """Resolve a relative path while blocking access outside the project root."""
    candidate = (PROJECT_ROOT / relative_path).resolve()

    if not candidate.is_relative_to(PROJECT_ROOT):
        raise ValueError("Access outside MAHY_PROJECT_ROOT is not allowed.")

    return candidate


@mcp.tool()
def project_root() -> str:
    """Return the configured project root path."""
    return str(PROJECT_ROOT)


@mcp.tool()
def list_directory(relative_path: str = ".") -> list[dict[str, str]]:
    """List files and folders within a project-relative directory."""
    directory = resolve_project_path(relative_path)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {relative_path}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {relative_path}")

    entries = []
    for item in sorted(directory.iterdir(), key=lambda path: (not path.is_dir(), path.name)):
        entries.append(
            {
                "name": item.name,
                "path": str(item.relative_to(PROJECT_ROOT)),
                "type": "directory" if item.is_dir() else "file",
            }
        )

    return entries[:MAX_RESULTS]


@mcp.tool()
def read_text_file(relative_path: str) -> str:
    """Read a UTF-8 text or Markdown file inside the project."""
    file_path = resolve_project_path(relative_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {relative_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Not a file: {relative_path}")

    if file_path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(
            f"File is larger than the {MAX_FILE_BYTES}-byte read limit: {relative_path}"
        )

    return file_path.read_text(encoding="utf-8")


@mcp.tool()
def search_text(query: str, relative_path: str = ".") -> list[dict[str, object]]:
    """Search UTF-8 .md, .txt, .py, .json, and .yaml files for a text query."""
    search_root = resolve_project_path(relative_path)

    if not search_root.exists():
        raise FileNotFoundError(f"Path not found: {relative_path}")

    allowed_suffixes = {".md", ".txt", ".py", ".json", ".yaml", ".yml"}
    matches: list[dict[str, object]] = []

    for file_path in search_root.rglob("*"):
        if len(matches) >= MAX_RESULTS:
            break

        if not file_path.is_file() or file_path.suffix.lower() not in allowed_suffixes:
            continue

        if file_path.stat().st_size > MAX_FILE_BYTES:
            continue

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if query.casefold() in line.casefold():
                matches.append(
                    {
                        "path": str(file_path.relative_to(PROJECT_ROOT)),
                        "line": line_number,
                        "text": line.strip(),
                    }
                )

                if len(matches) >= MAX_RESULTS:
                    break

    return matches


if __name__ == "__main__":
    mcp.run()