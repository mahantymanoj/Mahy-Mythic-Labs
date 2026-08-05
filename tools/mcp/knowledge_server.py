"""Read-only MCP server for the Mahy Mythic Labs knowledge base."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Mahy Mythic Labs Knowledge Base",
    instructions=(
        "Read-only access to the project knowledge base. "
        "Use sources critically and distinguish evidence from interpretation."
    ),
)

PROJECT_ROOT = Path(os.getenv("MAHY_PROJECT_ROOT", ".")).resolve()
KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge_base"
MAX_DOCUMENT_BYTES = 200_000
MAX_RESULTS = 50


def resolve_knowledge_path(relative_path: str) -> Path:
    """Resolve a path while blocking access outside knowledge_base."""
    candidate = (KNOWLEDGE_ROOT / relative_path).resolve()

    if not candidate.is_relative_to(KNOWLEDGE_ROOT.resolve()):
        raise ValueError("Access outside knowledge_base is not allowed.")

    return candidate


@mcp.tool()
def list_knowledge_categories() -> list[str]:
    """List top-level knowledge-base categories."""
    if not KNOWLEDGE_ROOT.exists():
        return []

    return sorted(
        item.name
        for item in KNOWLEDGE_ROOT.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    )


@mcp.tool()
def list_knowledge_documents(category: str = "") -> list[str]:
    """List Markdown documents within a knowledge-base category."""
    directory = resolve_knowledge_path(category or ".")

    if not directory.exists():
        raise FileNotFoundError(f"Knowledge category not found: {category}")

    return sorted(
        str(path.relative_to(KNOWLEDGE_ROOT))
        for path in directory.rglob("*.md")
        if path.is_file()
    )[:MAX_RESULTS]


@mcp.tool()
def read_knowledge_document(relative_path: str) -> str:
    """Read one Markdown knowledge-base document."""
    document = resolve_knowledge_path(relative_path)

    if not document.exists():
        raise FileNotFoundError(f"Knowledge document not found: {relative_path}")

    if document.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError(f"Knowledge document exceeds size limit: {relative_path}")

    return document.read_text(encoding="utf-8")


@mcp.tool()
def search_knowledge(query: str, category: str = "") -> list[dict[str, object]]:
    """Search Markdown knowledge documents and return matching lines."""
    search_root = resolve_knowledge_path(category or ".")

    if not search_root.exists():
        raise FileNotFoundError(f"Knowledge category not found: {category}")

    results: list[dict[str, object]] = []

    for document in search_root.rglob("*.md"):
        if len(results) >= MAX_RESULTS or document.stat().st_size > MAX_DOCUMENT_BYTES:
            continue

        for line_number, line in enumerate(
            document.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if query.casefold() in line.casefold():
                results.append(
                    {
                        "document": str(document.relative_to(KNOWLEDGE_ROOT)),
                        "line": line_number,
                        "text": line.strip(),
                    }
                )

                if len(results) >= MAX_RESULTS:
                    break

    return results


if __name__ == "__main__":
    mcp.run()