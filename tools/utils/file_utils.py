"""Safe file helpers for Mahy Mythic Labs production tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_directory(path: str | Path) -> Path:
    """Create a directory and its parents when they do not already exist."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_text(path: str | Path) -> str:
    """Read a UTF-8 text file."""
    return Path(path).read_text(encoding="utf-8")


def write_text(
    path: str | Path,
    content: str,
    *,
    overwrite: bool = False,
) -> Path:
    """Write UTF-8 text, refusing to overwrite unless explicitly approved."""
    output_path = Path(path)

    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {output_path}. "
            "Pass overwrite=True only when replacement is intentional."
        )

    ensure_directory(output_path.parent)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def read_json(path: str | Path) -> dict[str, Any]:
    """Read a JSON object from a UTF-8 file."""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(
    path: str | Path,
    data: dict[str, Any],
    *,
    overwrite: bool = False,
) -> Path:
    """Write formatted JSON without silently overwriting existing files."""
    content = json.dumps(data, indent=2, ensure_ascii=False)
    return write_text(path, f"{content}\n", overwrite=overwrite)


def safe_relative_path(root: str | Path, relative_path: str | Path) -> Path:
    """Resolve a project-relative path while blocking directory traversal."""
    root_path = Path(root).resolve()
    candidate = (root_path / relative_path).resolve()

    if not candidate.is_relative_to(root_path):
        raise ValueError("Path must remain inside the configured project root.")

    return candidate


def list_files(
    directory: str | Path,
    *,
    suffixes: tuple[str, ...] = (),
) -> list[Path]:
    """Return sorted files, optionally filtered by filename suffix."""
    root = Path(directory)

    if not root.exists():
        return []

    files = [path for path in root.rglob("*") if path.is_file()]

    if suffixes:
        normalized_suffixes = tuple(suffix.lower() for suffix in suffixes)
        files = [
            path
            for path in files
            if path.suffix.lower() in normalized_suffixes
        ]

    return sorted(files)video_client.py