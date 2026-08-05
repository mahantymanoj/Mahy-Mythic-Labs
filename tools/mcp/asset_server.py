"""Read-only MCP server for Mahy Mythic Labs asset and license records."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Mahy Mythic Labs Asset Library",
    instructions=(
        "Read-only access to asset, license, and reference records. "
        "An asset is not approved for use unless its rights and status are documented."
    ),
)

PROJECT_ROOT = Path(os.getenv("MAHY_PROJECT_ROOT", ".")).resolve()
ASSETS_ROOT = PROJECT_ROOT / "assets"
MAX_FILE_BYTES = 200_000
MAX_RESULTS = 100


def read_if_present(relative_path: str) -> str:
    """Read a project-relative text file if it exists."""
    file_path = PROJECT_ROOT / relative_path

    if not file_path.exists():
        return f"File not found: {relative_path}"

    if file_path.stat().st_size > MAX_FILE_BYTES:
        return f"File exceeds read limit: {relative_path}"

    return file_path.read_text(encoding="utf-8")


@mcp.tool()
def list_asset_categories() -> list[str]:
    """List top-level asset-library categories."""
    if not ASSETS_ROOT.exists():
        return []

    return sorted(
        item.name
        for item in ASSETS_ROOT.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    )


@mcp.tool()
def read_asset_database() -> str:
    """Read the central asset database."""
    return read_if_present("assets/asset_database.md")


@mcp.tool()
def read_license_tracker() -> str:
    """Read the central third-party asset license tracker."""
    return read_if_present("assets/licenses/asset_license_tracker.md")


@mcp.tool()
def find_asset(asset_id_or_name: str) -> list[str]:
    """Find matching entries in the Markdown asset database."""
    database = read_if_present("assets/asset_database.md")

    if database.startswith("File not found") or database.startswith("File exceeds"):
        return [database]

    matches = [
        line
        for line in database.splitlines()
        if asset_id_or_name.casefold() in line.casefold()
    ]
    return matches[:MAX_RESULTS]


@mcp.tool()
def list_assets_in_category(category: str) -> list[str]:
    """List files in one top-level asset category without reading binary data."""
    category_path = (ASSETS_ROOT / category).resolve()

    if not category_path.is_relative_to(ASSETS_ROOT.resolve()):
        raise ValueError("Access outside assets is not allowed.")

    if not category_path.exists() or not category_path.is_dir():
        raise FileNotFoundError(f"Asset category not found: {category}")

    return sorted(
        str(path.relative_to(ASSETS_ROOT))
        for path in category_path.rglob("*")
        if path.is_file()
    )[:MAX_RESULTS]


if __name__ == "__main__":
    mcp.run()