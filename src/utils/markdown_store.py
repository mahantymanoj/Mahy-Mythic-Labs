"""
src/utils/markdown_store.py

Shared helpers for persisting reusable domain content (research
findings, character sheets) as markdown files with YAML frontmatter.

This is what lets the pipeline cache work on disk and reuse it for a
future episode on the same topic or with the same character, instead
of re-running research or re-designing a character from scratch.

Python
------
>=3.11
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import frontmatter


# ==============================================================================
# Slug
# ==============================================================================


def slugify(text: str) -> str:
    """
    Convert text into a filesystem-safe, lowercase slug.

    Example
    -------
    "Black Holes & Neutron Stars" -> "black-holes-neutron-stars"
    """

    text = text.strip().lower()

    text = re.sub(r"[^a-z0-9]+", "-", text)

    return text.strip("-") or "untitled"


# ==============================================================================
# Markdown + Frontmatter I/O
# ==============================================================================


def write_markdown(
    path: Path,
    *,
    metadata: dict[str, Any],
    body: str,
) -> Path:
    """
    Write a markdown file with YAML frontmatter.

    Parameters
    ----------
    path:
        Destination file path.

    metadata:
        Frontmatter fields (must be YAML-serializable).

    body:
        Markdown body content.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    post = frontmatter.Post(
        body,
        **metadata,
    )

    path.write_text(
        frontmatter.dumps(post),
        encoding="utf-8",
    )

    return path


def read_markdown(
    path: Path,
) -> tuple[dict[str, Any], str]:
    """
    Read a markdown file with YAML frontmatter.

    Returns
    -------
    tuple[dict, str]
        (frontmatter metadata, markdown body)
    """

    post = frontmatter.load(path)

    return dict(post.metadata), post.content


def find_markdown_by_slug(
    directory: Path,
    slug: str,
) -> Path | None:
    """
    Return the markdown file for a slug, if it exists in directory.
    """

    candidate = directory / f"{slug}.md"

    if candidate.is_file():
        return candidate

    return None
