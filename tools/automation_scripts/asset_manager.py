"""Validate asset names and prepare asset metadata records."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


FILENAME_PATTERN = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*-v\d{2}\.[a-z0-9]+$"
)


def validate_filename(filename: str) -> tuple[bool, str]:
    """Check the Mahy Mythic Labs lowercase kebab-case asset convention."""
    if FILENAME_PATTERN.fullmatch(filename):
        return True, "Valid filename."

    return (
        False,
        "Invalid filename. Use lowercase kebab case ending in a version number, "
        "for example: ep001-antikythera-gear-image-v01.png",
    )


def create_asset_record(
    asset_id: str,
    asset_name: str,
    category: str,
    source: str,
    license_id: str,
    location: str,
) -> str:
    """Return one Markdown table row for assets/asset_database.md."""
    today = date.today().isoformat()
    return (
        f"| {asset_id} | {asset_name} | {category} | — | Pending | "
        f"{source} | {license_id} | {location} | — | {today} | — |"
    )


def append_record(database_path: Path, record: str) -> None:
    """Append a record only when the target Markdown database already exists."""
    if not database_path.exists():
        raise FileNotFoundError(
            f"Asset database not found: {database_path}. Create it before registering assets."
        )

    existing_content = database_path.read_text(encoding="utf-8")
    if record in existing_content:
        print("Record already exists; no change made.")
        return

    with database_path.open("a", encoding="utf-8") as file:
        file.write(f"\n{record}\n")

    print(f"Asset record added: {database_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mahy Mythic Labs asset manager.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("filename")

    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("asset_id")
    register_parser.add_argument("asset_name")
    register_parser.add_argument("category")
    register_parser.add_argument("source")
    register_parser.add_argument("license_id")
    register_parser.add_argument("location")
    register_parser.add_argument(
        "--database",
        default="assets/asset_database.md",
        help="Path to the Markdown asset database.",
    )

    args = parser.parse_args()

    if args.command == "validate":
        is_valid, message = validate_filename(args.filename)
        print(message)
        raise SystemExit(0 if is_valid else 1)

    record = create_asset_record(
        args.asset_id,
        args.asset_name,
        args.category,
        args.source,
        args.license_id,
        args.location,
    )
    append_record(Path(args.database), record)


if __name__ == "__main__":
    main()