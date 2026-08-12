"""
src/models/script.py

Script domain models.

A Script is the narrative blueprint for an Episode.

Hierarchy
---------
Project
    └── Episode
            └── Script
                    ├── ScriptSection
                    │       └── ScriptDialogue
                    └── (hook / call_to_action)

Python
------
>=3.11

Pydantic
---------
>=2.x
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import Field, field_validator

from .base import EntityModel, ValueModel


# ==============================================================================
# Enums
# ==============================================================================


class ScriptStatus(str, Enum):
    """Script lifecycle."""

    DRAFT = "draft"
    WRITING = "writing"
    REVIEW = "review"
    APPROVED = "approved"
    LOCKED = "locked"
    ARCHIVED = "archived"


class SectionType(str, Enum):
    """Script section classification."""

    INTRO = "intro"
    NARRATION = "narration"
    DIALOGUE = "dialogue"
    SCENE = "scene"
    TRANSITION = "transition"
    ACTION = "action"
    OUTRO = "outro"


# ==============================================================================
# ScriptDialogue — must be defined BEFORE ScriptSection uses it
# ==============================================================================


class ScriptDialogue(ValueModel):
    """
    A single spoken dialogue block within a script section.
    Immutable value object — compared by value.
    """

    character: str = Field(
        min_length=1,
        max_length=200,
        description="Speaking character name.",
    )

    text: str = Field(
        min_length=1,
        description="Dialogue text.",
    )

    emotion: Optional[str] = Field(
        default=None,
        description="Emotional direction for delivery.",
    )

    direction: Optional[str] = Field(
        default=None,
        description="Stage/camera direction.",
    )

    estimated_duration_seconds: float = Field(
        default=0.0,
        ge=0,
        description="Estimated spoken duration.",
    )

    @field_validator("character", "text")
    @classmethod
    def _not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty.")
        return value

    def __str__(self) -> str:
        return f"{self.character}: {self.text[:60]}..."


# ==============================================================================
# ScriptSection — uses ScriptDialogue (defined above)
# ==============================================================================


class ScriptSection(ValueModel):
    """
    Represents one logical section of a script.

    A section may contain narration, dialogue, actions,
    and scene directions.
    """

    section_number: int = Field(
        ge=1,
        description="Section order within the script.",
    )

    section_type: SectionType = Field(
        default=SectionType.NARRATION,
    )

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    narration: Optional[str] = None

    description: Optional[str] = None

    dialogues: List[ScriptDialogue] = Field(
        default_factory=list,
        description="Dialogue blocks.",
    )

    action: Optional[str] = None

    transition: Optional[str] = None

    estimated_duration_seconds: float = Field(
        default=0.0,
        ge=0,
    )

    notes: Optional[str] = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Section title cannot be empty.")
        return value

    # ------------------------------------------------------------------
    # Dialogue Management
    # ------------------------------------------------------------------

    def add_dialogue(self, dialogue: ScriptDialogue) -> "ScriptSection":
        """Return a new section with an additional dialogue."""
        return self.replace(dialogues=[*self.dialogues, dialogue])

    def remove_dialogue(self, index: int) -> "ScriptSection":
        """Return a new section without the specified dialogue."""
        if not (0 <= index < len(self.dialogues)):
            return self
        updated = list(self.dialogues)
        updated.pop(index)
        return self.replace(dialogues=updated)

    def update_dialogue(self, index: int, dialogue: ScriptDialogue) -> "ScriptSection":
        """Replace an existing dialogue."""
        if not (0 <= index < len(self.dialogues)):
            return self
        updated = list(self.dialogues)
        updated[index] = dialogue
        return self.replace(dialogues=updated)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def dialogue_count(self) -> int:
        return len(self.dialogues)

    @property
    def has_narration(self) -> bool:
        return bool(self.narration)

    @property
    def has_dialogue(self) -> bool:
        return bool(self.dialogues)

    @property
    def estimated_duration_minutes(self) -> float:
        return round(self.estimated_duration_seconds / 60, 2)

    def __str__(self) -> str:
        return f"Section {self.section_number}: {self.title}"

    def __repr__(self) -> str:
        return (
            "ScriptSection("
            f"section_number={self.section_number}, "
            f"type={self.section_type.value!r}, "
            f"title={self.title!r}"
            ")"
        )


# ==============================================================================
# Script Entity — owns identity and lifecycle
# ==============================================================================


class Script(EntityModel):
    """
    The complete narrative script for one episode.

    Uses EntityModel because scripts have persistent identity
    and are tracked through the production lifecycle.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    title: str = Field(
        min_length=1,
        max_length=300,
        description="Script title.",
    )

    hook: str = Field(
        default="",
        description="Opening hook that grabs viewer attention.",
    )

    call_to_action: str = Field(
        default="",
        description="Closing call to action.",
    )

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    sections: List[ScriptSection] = Field(
        default_factory=list,
        description="Ordered list of script sections.",
    )

    status: ScriptStatus = Field(
        default=ScriptStatus.DRAFT,
    )

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    total_estimated_duration: float = Field(
        default=0.0,
        ge=0,
        description="Total estimated duration in seconds.",
    )

    word_count: int = Field(
        default=0,
        ge=0,
    )

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    notes: Optional[str] = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Script title cannot be empty.")
        return value

    # ------------------------------------------------------------------
    # Section Management
    # ------------------------------------------------------------------

    def add_section(self, section: ScriptSection) -> None:
        """Append a section and refresh duration estimate."""
        self.sections.append(section)
        self._refresh_duration()
        self.touch()

    def remove_section(self, section_number: int) -> None:
        """Remove section by number."""
        self.sections = [
            s for s in self.sections
            if s.section_number != section_number
        ]
        self._refresh_duration()
        self.touch()

    def _refresh_duration(self) -> None:
        """Recalculate total estimated duration from sections."""
        self.total_estimated_duration = sum(
            s.estimated_duration_seconds for s in self.sections
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def approve(self) -> None:
        self.status = ScriptStatus.APPROVED
        self.touch()

    def lock(self) -> None:
        self.status = ScriptStatus.LOCKED
        self.touch()

    def archive(self) -> None:
        self.status = ScriptStatus.ARCHIVED
        self.touch()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def section_count(self) -> int:
        return len(self.sections)

    @property
    def is_approved(self) -> bool:
        return self.status == ScriptStatus.APPROVED

    @property
    def is_locked(self) -> bool:
        return self.status == ScriptStatus.LOCKED

    @property
    def duration_minutes(self) -> float:
        return round(self.total_estimated_duration / 60, 2)

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            "Script("
            f"id={self.id}, "
            f"title={self.title!r}, "
            f"sections={self.section_count}, "
            f"status={self.status.value!r}"
            ")"
        )

        # ------------------------------------------------------------------
    # Metadata Helpers
    # ------------------------------------------------------------------

    def add_tag(
        self,
        tag: str,
    ) -> None:
        """
        Add a unique tag.
        """

        tag = tag.strip()

        if tag and tag not in self.metadata.setdefault("tags", []):
            self.metadata["tags"].append(tag)

        self.touch()

    def remove_tag(
        self,
        tag: str,
    ) -> None:
        """
        Remove a tag.
        """

        tags = self.metadata.setdefault("tags", [])

        if tag in tags:
            tags.remove(tag)

        self.touch()

    def update_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Update metadata.
        """

        self.metadata[key] = value
        self.touch()

    def remove_metadata(
        self,
        key: str,
    ) -> None:
        """
        Remove metadata entry.
        """

        self.metadata.pop(key, None)
        self.touch()

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def rename(
        self,
        title: str,
    ) -> None:
        """
        Rename script.
        """

        self.title = title.strip()
        self.touch()

    def reset_review(self) -> None:
        """
        Reset review workflow.
        """

        self.status = ScriptStatus.DRAFT
        self.touch()

    def clone_metadata(self) -> dict[str, Any]:
        """
        Return a shallow copy of metadata.
        """

        return dict(self.metadata)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def dialogue_count(self) -> int:
        """
        Total dialogue blocks.
        """

        return sum(
            section.dialogue_count
            for section in self.sections
        )

    @property
    def narration_count(self) -> int:
        """
        Number of narration sections.
        """

        return sum(
            section.has_narration
            for section in self.sections
        )

    @property
    def estimated_reading_minutes(self) -> float:
        """
        Estimated narration duration based on word count.
        """

        if self.word_count == 0:
            return 0.0

        return round(
            self.word_count / 150,
            2,
        )