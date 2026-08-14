"""
src/services/character_service.py

Character cache service for Mahy Mythic Labs Studio OS.

Persists Character entities (appearance, voice, personality,
continuity, references) as markdown files keyed by name, so a
recurring character (e.g. Lord Shiva, Einstein) can be reused
across episodes with an identical design and voice instead of
being redesigned from scratch every time.

Also keeps assets/characters/character_registry.md — the existing,
previously-manual character index documented in the production
bible — in sync with every saved character.

Python
------
>=3.11
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.constants import PROJECT_ROOT
from src.models.character import Character
from src.utils.markdown_store import (
    find_markdown_by_slug,
    read_markdown,
    slugify,
    write_markdown,
)

DEFAULT_CHARACTERS_DIRECTORY = PROJECT_ROOT / "assets" / "characters"
REGISTRY_FILE_NAME = "character_registry.md"

_REGISTRY_ROW = re.compile(
    r"^\|[ \t]*(?P<id>[^|\n]*)\|[ \t]*(?P<name>[^|\n]*)\|[ \t]*(?P<category>[^|\n]*)\|"
    r"[ \t]*(?P<context>[^|\n]*)\|[ \t]*(?P<first_episode>[^|\n]*)\|"
    r"[ \t]*(?P<status>[^|\n]*)\|[ \t]*(?P<reference_file>[^|\n]*)\|[ \t]*$",
    re.MULTILINE,
)


# ==============================================================================
# Character Cache Service
# ==============================================================================


class CharacterCacheService:
    """
    Reads and writes name-keyed character sheets.

    Unlike research (which is scoped to a project/episode), a saved
    Character keeps its identity (id, appearance, voice, personality)
    stable across reuse, since visual/voice continuity across episodes
    is exactly what reuse is for.
    """

    def __init__(
        self,
        *,
        characters_directory: Path | None = None,
    ) -> None:

        self.characters_directory = (
            characters_directory
            or DEFAULT_CHARACTERS_DIRECTORY
        )

    # ==================================================================
    # Lookup
    # ==================================================================

    def character_path(
        self,
        name: str,
    ) -> Path:
        """
        Return the file path for a character name (existing or not).
        """

        return self.characters_directory / f"{slugify(name)}.md"

    def find_character_path(
        self,
        name: str,
    ) -> Path | None:
        """
        Return the file path for a character name if it already exists.
        """

        return find_markdown_by_slug(
            self.characters_directory,
            slugify(name),
        )

    def has_character(
        self,
        name: str,
    ) -> bool:
        """
        Return True when a character with this name is already saved.
        """

        return self.find_character_path(name) is not None

    # ==================================================================
    # Save
    # ==================================================================

    def save(
        self,
        character: Character,
    ) -> Path:
        """
        Persist a character sheet, keyed by its canonical name.

        Also upserts a row for this character in the character registry.
        """

        path = self.character_path(character.canonical_name)

        metadata = character.model_dump(
            mode="json",
            exclude_none=True,
        )

        body = self._render_body(character)

        write_markdown(
            path,
            metadata=metadata,
            body=body,
        )

        self._upsert_registry_row(
            character=character,
            reference_file=path.relative_to(
                self.characters_directory.parent
            ).as_posix(),
        )

        return path

    # ==================================================================
    # Load
    # ==================================================================

    def load(
        self,
        name: str,
    ) -> Character | None:
        """
        Load a previously saved character by name.

        Returns None when nothing is cached for this name (the caller
        should fall back to designing a new character).
        """

        path = self.find_character_path(name)

        if path is None:
            return None

        metadata, _ = read_markdown(path)

        return Character.model_validate(metadata)

    def load_or_reuse(
        self,
        name: str,
        *,
        episode_id: str,
    ) -> Character | None:
        """
        Load a character and register a new episode appearance.

        This is the convenience entry point for the production
        pipeline: call it before designing a new character, and only
        fall through to character-design when it returns None.
        """

        character = self.load(name)

        if character is None:
            return None

        character.add_episode(episode_id)

        self.save(character)

        return character

    # ==================================================================
    # Body Rendering
    # ==================================================================

    @staticmethod
    def _render_body(
        character: Character,
    ) -> str:
        """
        Render a human-readable summary of the character.

        The frontmatter is the source of truth on load; this body is
        regenerated on every save purely for human readability.
        """

        parts = [f"# {character.canonical_name}", ""]

        if character.short_description:
            parts += [character.short_description, ""]

        if character.biography:
            parts += ["## Biography", "", character.biography, ""]

        parts += [
            "## Reusable Generation Prompt",
            "",
            "```text",
            character.generation_prompt(include_voice=True),
            "```",
            "",
        ]

        if character.episode_ids:
            parts += [
                "## Episodes",
                "",
                ", ".join(character.episode_ids),
                "",
            ]

        return "\n".join(parts).strip() + "\n"

    # ==================================================================
    # Registry Sync
    # ==================================================================

    def _registry_path(self) -> Path:

        return self.characters_directory / REGISTRY_FILE_NAME

    def _upsert_registry_row(
        self,
        *,
        character: Character,
        reference_file: str,
    ) -> None:
        """
        Insert or update this character's row in character_registry.md.

        Does nothing if the registry file does not exist, so this
        stays optional rather than a hard dependency.
        """

        registry_path = self._registry_path()

        if not registry_path.is_file():
            return

        text = registry_path.read_text(encoding="utf-8")

        rows = self._parse_registry_rows(text)

        rows = [
            row
            for row in rows
            if row["name"].strip().lower()
            != character.canonical_name.lower()
            and row["name"].strip() != "—"
        ]

        character_id = self._existing_character_id(
            text,
            character.canonical_name,
        ) or f"CHAR-{len(rows) + 1:03d}"

        rows.append(
            {
                "id": character_id,
                "name": character.canonical_name,
                "category": character.character_type,
                "context": (
                    character.historical_context
                    or character.cultural_context
                    or "—"
                ),
                "first_episode": character.first_episode_id or "—",
                "status": character.status,
                "reference_file": reference_file,
            }
        )

        new_text = self._render_registry_table(text, rows)

        registry_path.write_text(new_text, encoding="utf-8")

    @staticmethod
    def _parse_registry_rows(
        text: str,
    ) -> list[dict[str, str]]:

        rows: list[dict[str, str]] = []

        for match in _REGISTRY_ROW.finditer(text):

            values = {
                key: value.strip()
                for key, value in match.groupdict().items()
            }

            if values["id"].strip("-") in {"", "Character ID"}:
                continue

            rows.append(values)

        return rows

    @staticmethod
    def _existing_character_id(
        text: str,
        name: str,
    ) -> str | None:

        for match in _REGISTRY_ROW.finditer(text):

            if match.group("name").strip().lower() == name.lower():
                return match.group("id").strip()

        return None

    @staticmethod
    def _render_registry_table(
        text: str,
        rows: list[dict[str, str]],
    ) -> str:

        header = (
            "| Character ID | Name / Working Name | Category | "
            "Cultural / Historical Context | First Episode | Status | "
            "Reference File |"
        )

        separator = "| --- | --- | --- | --- | --- | --- | --- |"

        lines = [header, separator]

        for row in rows:

            lines.append(
                "| "
                + " | ".join(
                    [
                        row["id"],
                        row["name"],
                        row["category"],
                        row["context"],
                        row["first_episode"],
                        row["status"],
                        row["reference_file"],
                    ]
                )
                + " |"
            )

        table = "\n".join(lines)

        return _REGISTRY_TABLE_BLOCK.sub(
            table,
            text,
            count=1,
        )


_REGISTRY_TABLE_BLOCK = re.compile(
    r"\|\s*Character ID\s*\|.*?(?=\n\n|\n##|\Z)",
    re.DOTALL,
)
