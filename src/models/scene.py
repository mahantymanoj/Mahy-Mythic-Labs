"""
src/models/scene.py

Scene domain model.

A Scene represents one logical segment of an Episode.
A Scene contains one or more Shots and defines the
storytelling, environment, and visual continuity.

Hierarchy
---------
Project
    └── Episode
            └── Scene
                    └── Shot

Examples
--------
• Opening Scene
• Shiva Meditation Scene
• Cosmic Creation Scene
• Battlefield Scene
• Temple Interior Scene

Python
------
>=3.11

Pydantic
---------
>=2.x
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from .base import EntityModel


# ==============================================================================
# Enumerations
# ==============================================================================


class SceneType(str, Enum):
    """
    Scene classification.
    """

    INTRO = "intro"

    STORY = "story"

    FLASHBACK = "flashback"

    DIALOGUE = "dialogue"

    ACTION = "action"

    MONTAGE = "montage"

    TRANSITION = "transition"

    CLIMAX = "climax"

    ENDING = "ending"

    CREDITS = "credits"


class SceneStatus(str, Enum):
    """
    Scene lifecycle.
    """

    DRAFT = "draft"

    WRITING = "writing"

    READY = "ready"

    GENERATING = "generating"

    REVIEW = "review"

    APPROVED = "approved"

    COMPLETED = "completed"

    ARCHIVED = "archived"


class SceneMood(str, Enum):
    """
    Emotional tone.
    """

    PEACEFUL = "peaceful"

    MYSTICAL = "mystical"

    DRAMATIC = "dramatic"

    DARK = "dark"

    HOPEFUL = "hopeful"

    EPIC = "epic"

    EMOTIONAL = "emotional"

    SUSPENSE = "suspense"

    HORROR = "horror"

    DIVINE = "divine"

# ==============================================================================
# Scene Entity
# ==============================================================================


class Scene(EntityModel):
    """
    Represents a single scene within an episode.

    A scene is composed of one or more shots and defines a
    continuous portion of the story.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    project_id: UUID = Field(
        description="Associated project."
    )

    episode_id: UUID = Field(
        description="Associated episode."
    )

    # Store only Shot IDs to avoid circular imports.
    shot_ids: list[UUID] = Field(
        default_factory=list,
        description="Ordered shot identifiers."
    )

    # ------------------------------------------------------------------
    # Ordering
    # ------------------------------------------------------------------

    scene_number: int = Field(
        ge=1,
        description="Scene sequence number."
    )

    chapter_number: int | None = Field(
        default=None,
        ge=1,
        description="Optional chapter number."
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    scene_type: SceneType = Field(
        default=SceneType.STORY,
    )

    status: SceneStatus = Field(
        default=SceneStatus.DRAFT,
    )

    mood: SceneMood = Field(
        default=SceneMood.MYSTICAL,
    )

    # ------------------------------------------------------------------
    # Story Information
    # ------------------------------------------------------------------

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    summary: str = Field(
        min_length=1,
    )

    narration: str | None = Field(
        default=None,
    )

    dialogue: str | None = Field(
        default=None,
    )

    objective: str | None = Field(
        default=None,
        description="Purpose of the scene."
    )

    # ------------------------------------------------------------------
    # Visual Information
    # ------------------------------------------------------------------

    location: str | None = Field(
        default=None,
    )

    environment: str | None = Field(
        default=None,
    )

    time_of_day: str | None = Field(
        default=None,
    )

    weather: str | None = Field(
        default=None,
    )

    visual_style: str | None = Field(
        default=None,
    )

    color_palette: list[str] = Field(
        default_factory=list,
    )

    # ------------------------------------------------------------------
    # Production
    # ------------------------------------------------------------------

    estimated_duration_seconds: float = Field(
        default=0.0,
        ge=0,
    )

    actual_duration_seconds: float | None = Field(
        default=None,
        ge=0,
    )

    target_shot_count: int = Field(
        default=0,
        ge=0,
    )

    completed_shots: int = Field(
        default=0,
        ge=0,
    )

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------

    background_music: str | None = Field(
        default=None,
    )

    ambience: str | None = Field(
        default=None,
    )

    narration_voice: str | None = Field(
        default=None,
    )

    sound_effects: list[str] = Field(
        default_factory=list,
    )

    # ------------------------------------------------------------------
    # AI Generation
    # ------------------------------------------------------------------

    image_prompt: str | None = Field(
        default=None,
    )

    video_prompt: str | None = Field(
        default=None,
    )

    negative_prompt: str | None = Field(
        default=None,
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    tags: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

        # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """
        Validate scene title.
        """
        value = value.strip()

        if not value:
            raise ValueError(
                "Scene title cannot be empty."
            )

        return value

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        """
        Validate scene summary.
        """
        value = value.strip()

        if not value:
            raise ValueError(
                "Scene summary cannot be empty."
            )

        return value

    # ------------------------------------------------------------------
    # Business Validation
    # ------------------------------------------------------------------

    def validate_state(self) -> None:
        """
        Validate scene consistency.
        """

        if self.completed_shots > self.target_shot_count:
            raise ValueError(
                "Completed shots cannot exceed target shots."
            )

        if (
            self.actual_duration_seconds is not None
            and self.actual_duration_seconds < 0
        ):
            raise ValueError(
                "Duration cannot be negative."
            )

    # ------------------------------------------------------------------
    # Shot Management
    # ------------------------------------------------------------------

    def add_shot(
        self,
        shot_id: UUID,
    ) -> None:
        """
        Add a shot to this scene.
        """

        if shot_id not in self.shot_ids:
            self.shot_ids.append(shot_id)
            self.target_shot_count = len(self.shot_ids)
            self.touch()

    def remove_shot(
        self,
        shot_id: UUID,
    ) -> None:
        """
        Remove a shot.
        """

        if shot_id in self.shot_ids:
            self.shot_ids.remove(shot_id)
            self.target_shot_count = len(self.shot_ids)
            self.touch()

    def clear_shots(self) -> None:
        """
        Remove all shots.
        """

        self.shot_ids.clear()
        self.target_shot_count = 0
        self.completed_shots = 0
        self.touch()

    def mark_shot_completed(self) -> None:
        """
        Increment completed shot count.
        """

        if self.completed_shots < self.target_shot_count:
            self.completed_shots += 1

        self.validate_state()
        self.touch()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_writing(self) -> None:
        self.status = SceneStatus.WRITING
        self.touch()

    def mark_ready(self) -> None:
        self.validate_state()
        self.status = SceneStatus.READY
        self.touch()

    def start_generation(self) -> None:
        self.status = SceneStatus.GENERATING
        self.touch()

    def mark_review(self) -> None:
        self.status = SceneStatus.REVIEW
        self.touch()

    def approve(self) -> None:
        self.status = SceneStatus.APPROVED
        self.touch()

    def complete(self) -> None:
        self.status = SceneStatus.COMPLETED
        self.touch()

    def archive(self) -> None:
        self.status = SceneStatus.ARCHIVED
        self.touch()

    # ------------------------------------------------------------------
    # Metadata Helpers
    # ------------------------------------------------------------------

    def add_tag(
        self,
        tag: str,
    ) -> None:
        """
        Add a tag.
        """

        tag = tag.strip()

        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(
        self,
        tag: str,
    ) -> None:
        """
        Remove a tag.
        """

        if tag in self.tags:
            self.tags.remove(tag)
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
    # Statistics
    # ------------------------------------------------------------------

    @property
    def shot_count(self) -> int:
        """
        Total number of shots.
        """
        return len(self.shot_ids)

    @property
    def remaining_shots(self) -> int:
        """
        Number of remaining shots.
        """
        return max(
            0,
            self.target_shot_count - self.completed_shots,
        )

    @property
    def completion_percentage(self) -> float:
        """
        Scene completion percentage.
        """

        if self.target_shot_count == 0:
            return 0.0

        return round(
            (self.completed_shots / self.target_shot_count) * 100,
            2,
        )

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def has_narration(self) -> bool:
        return bool(self.narration)

    @property
    def has_dialogue(self) -> bool:
        return bool(self.dialogue)

    @property
    def has_music(self) -> bool:
        return bool(self.background_music)

    @property
    def has_sound_effects(self) -> bool:
        return len(self.sound_effects) > 0

    @property
    def has_image_prompt(self) -> bool:
        return bool(self.image_prompt)

    @property
    def has_video_prompt(self) -> bool:
        return bool(self.video_prompt)

    @property
    def is_ready(self) -> bool:
        return self.status == SceneStatus.READY

    @property
    def is_completed(self) -> bool:
        return self.status == SceneStatus.COMPLETED

    @property
    def is_archived(self) -> bool:
        return self.status == SceneStatus.ARCHIVED

    @property
    def duration_minutes(self) -> float:
        """
        Estimated duration in minutes.
        """

        return round(
            self.estimated_duration_seconds / 60,
            2,
        )

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def rename(
        self,
        title: str,
    ) -> None:
        """
        Rename scene.
        """

        self.title = title.strip()
        self.touch()

    def clone_metadata(self) -> dict[str, Any]:
        """
        Return a copy of metadata.
        """

        return dict(self.metadata)

    def reset_progress(self) -> None:
        """
        Reset production progress.
        """

        self.completed_shots = 0
        self.status = SceneStatus.DRAFT
        self.touch()

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"Scene {self.scene_number}: "
            f"{self.title}"
        )

    def __repr__(self) -> str:
        return (
            "Scene("
            f"id={self.id}, "
            f"scene_number={self.scene_number}, "
            f"title={self.title!r}, "
            f"status={self.status.value!r}"
            ")"
        )