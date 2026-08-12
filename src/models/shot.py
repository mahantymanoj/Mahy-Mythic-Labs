"""
src/models/shot.py

Shot domain model.

A Shot is the smallest production unit within a Scene.

A Scene consists of one or more Shots.

Each Shot contains the complete cinematic specification
required to generate AI images, videos, narration,
and final rendered assets.

Hierarchy
---------
Project
    └── Episode
            └── Scene
                    └── Shot

Python
------
>=3.11

Pydantic
---------
>=2.x
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from .base import EntityModel

# Components — import using the ACTUAL class names from each module
from .components.audio import AudioSettings
from .components.camera import CameraSettings
from .components.character_appearance import CharacterAppearance
from .components.composition import CompositionSettings
from .components.effects import EffectsSettings
from .components.environment import EnvironmentSettings
from .components.lighting import LightingSettings
from .components.prompt import PromptSet
from .components.render import RenderSettings
from .components.transition import TransitionSettings
from .components.visual_style import VisualStyleSettings


# ==============================================================================
# Enumerations
# ==============================================================================


class ShotType(str, Enum):
    """Cinematic shot classification."""

    ESTABLISHING = "establishing"
    WIDE = "wide"
    FULL = "full"
    MEDIUM = "medium"
    MEDIUM_CLOSE = "medium_close"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE = "extreme_close"
    OVER_SHOULDER = "over_shoulder"
    POV = "pov"
    INSERT = "insert"
    CUTAWAY = "cutaway"
    AERIAL = "aerial"


class ShotStatus(str, Enum):
    """Shot lifecycle."""

    DRAFT = "draft"
    READY = "ready"
    GENERATING = "generating"
    REVIEW = "review"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"


class CameraMovement(str, Enum):
    """
    Coarse camera movement enum used on the Shot level.
    Fine-grained movement is handled by CameraSettings.movement.
    """

    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    DOLLY = "dolly"
    TRUCK = "truck"
    CRANE = "crane"
    ZOOM = "zoom"
    ORBIT = "orbit"
    HANDHELD = "handheld"
    FPV = "fpv"


# ==============================================================================
# Shot Entity
# ==============================================================================


class Shot(EntityModel):
    """
    Represents a single cinematic shot.

    A Shot is the smallest production unit of a Scene and contains
    all information required for AI image/video generation.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    project_id: UUID = Field(description="Associated project.")
    episode_id: UUID = Field(description="Associated episode.")
    scene_id: UUID = Field(description="Parent scene.")

    generation_id: Optional[UUID] = Field(
        default=None,
        description="Latest generation job ID.",
    )

    asset_ids: list[UUID] = Field(
        default_factory=list,
        description="Generated asset IDs.",
    )

    character_ids: list[UUID] = Field(
        default_factory=list,
        description="Character UUIDs appearing in this shot.",
    )

    # ------------------------------------------------------------------
    # Ordering
    # ------------------------------------------------------------------

    shot_number: int = Field(ge=1, description="Shot number within its scene.")

    sequence: int = Field(
        default=1,
        ge=1,
        description="Global execution sequence across scenes.",
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    shot_type: ShotType = Field(default=ShotType.MEDIUM)

    status: ShotStatus = Field(default=ShotStatus.DRAFT)

    # BUG FIX: removed Shot-level camera_movement field.
    # The authoritative camera movement lives in CameraSettings.movement
    # to avoid duplicating and potentially contradicting it.

    # ------------------------------------------------------------------
    # Story
    # ------------------------------------------------------------------

    title: str = Field(min_length=1, max_length=200)

    description: str = Field(
        min_length=1,
        description="Visual description of what happens in the shot.",
    )

    narration: Optional[str] = None
    dialogue: Optional[str] = None
    action: Optional[str] = None
    emotion: Optional[str] = None
    objective: Optional[str] = None

    # ------------------------------------------------------------------
    # Timing
    # BUG FIX: changed ge=0 to gt=0 so the field constraint matches
    # validate_state() which also requires duration > 0. ge=0 previously
    # allowed 0.0 at the Pydantic level but validate_state() would then
    # raise at runtime — an inconsistency.
    # ------------------------------------------------------------------

    duration_seconds: float = Field(
        default=5.0,
        gt=0,
        description="Shot duration in seconds.",
    )

    # BUG FIX: removed the standalone fps field. fps is already defined
    # inside CameraSettings and RenderSettings. Having a third fps field
    # directly on Shot creates three potential sources of truth that can
    # silently disagree. Access fps via shot.camera.fps or shot.render.fps.

    # ------------------------------------------------------------------
    # Cinematic Components
    # BUG FIX: all field types now use the correct class names:
    #   Audio           -> AudioSettings
    #   Camera          -> CameraSettings
    #   Composition     -> CompositionSettings
    #   Effects         -> EffectsSettings
    #   Environment     -> EnvironmentSettings
    #   Lighting        -> LightingSettings
    #   Render          -> RenderSettings
    #   Transition      -> TransitionSettings
    #   VisualStyle     -> VisualStyleSettings
    # The previous code imported and used wrong names (Audio, Camera, etc.)
    # which do not exist in the component modules.
    # ------------------------------------------------------------------

    camera: CameraSettings = Field(default_factory=CameraSettings)
    lighting: LightingSettings = Field(default_factory=LightingSettings)
    environment: EnvironmentSettings = Field(default_factory=EnvironmentSettings)
    composition: CompositionSettings = Field(default_factory=CompositionSettings)
    visual_style: VisualStyleSettings = Field(default_factory=VisualStyleSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    render: RenderSettings = Field(default_factory=RenderSettings)
    transition: TransitionSettings = Field(default_factory=TransitionSettings)
    effects: EffectsSettings = Field(default_factory=EffectsSettings)
    prompt: PromptSet = Field(default_factory=PromptSet)

    # ------------------------------------------------------------------
    # Characters in this shot
    # ------------------------------------------------------------------

    characters: list[CharacterAppearance] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # AI Generation overrides
    # These allow the Director to override the structured prompt fields
    # with a raw string prompt for special cases.
    # ------------------------------------------------------------------

    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    model_name: Optional[str] = None

    # ------------------------------------------------------------------
    # Production
    # ------------------------------------------------------------------

    generation_attempts: int = Field(default=0, ge=0)

    approved: bool = False

    rating: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
        description="Production quality rating (0–10).",
    )

    notes: Optional[str] = None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Strip whitespace and reject empty titles."""
        value = value.strip()
        if not value:
            raise ValueError("Shot title cannot be empty.")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        """Strip whitespace and reject empty descriptions."""
        value = value.strip()
        if not value:
            raise ValueError("Shot description cannot be empty.")
        return value

    @field_validator("emotion", "objective", "narration", "dialogue", "action", mode="before")
    @classmethod
    def strip_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        """Normalise optional string fields — convert empty string to None."""
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None

    @model_validator(mode="after")
    def validate_state(self) -> "Shot":
        """
        Cross-field business rule validation.
        Called automatically by Pydantic after all field validators.
        """
        if self.rating is not None and not (0 <= self.rating <= 10):
            raise ValueError("Rating must be between 0 and 10.")
        return self

    # ------------------------------------------------------------------
    # Character Management
    # ------------------------------------------------------------------

    def add_character(self, character: CharacterAppearance) -> None:
        """Add a character appearance to this shot."""
        self.characters.append(character)
        self.touch()

    def remove_character(self, index: int) -> None:
        """Remove a character by list index."""
        if 0 <= index < len(self.characters):
            self.characters.pop(index)
            self.touch()

    # ------------------------------------------------------------------
    # Asset Management
    # ------------------------------------------------------------------

    def add_asset(self, asset_id: UUID) -> None:
        """Register a generated asset (deduplicates)."""
        if asset_id not in self.asset_ids:
            self.asset_ids.append(asset_id)
            self.touch()

    def remove_asset(self, asset_id: UUID) -> None:
        """Remove an asset reference."""
        if asset_id in self.asset_ids:
            self.asset_ids.remove(asset_id)
            self.touch()

    # ------------------------------------------------------------------
    # Generation Lifecycle
    # ------------------------------------------------------------------

    def mark_generating(self) -> None:
        """Transition to GENERATING and increment attempt counter."""
        self.status = ShotStatus.GENERATING
        self.generation_attempts += 1
        self.touch()

    def mark_review(self) -> None:
        """Move shot to REVIEW."""
        self.status = ShotStatus.REVIEW
        self.touch()

    def approve(self) -> None:
        """Approve this shot."""
        self.status = ShotStatus.APPROVED
        self.approved = True
        self.touch()

    def complete(self) -> None:
        """Mark shot as COMPLETED."""
        self.status = ShotStatus.COMPLETED
        self.touch()

    def fail(self) -> None:
        """Mark generation as FAILED."""
        self.status = ShotStatus.FAILED
        self.touch()

    def reset_generation(self) -> None:
        """Reset generation state back to DRAFT for a retry."""
        self.status = ShotStatus.DRAFT
        self.generation_attempts = 0
        self.generation_id = None
        # BUG FIX: was asset_ids.clear() which mutates the list in-place;
        # reassignment is cleaner and consistent with Pydantic's field tracking.
        self.asset_ids = []
        self.approved = False
        self.touch()

    # ------------------------------------------------------------------
    # Metadata Helpers
    # ------------------------------------------------------------------

    def add_tag(self, tag: str) -> None:
        """Add a tag (deduplicates)."""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.touch()

    def update_metadata(self, key: str, value: Any) -> None:
        """Set a metadata entry."""
        self.metadata[key] = value
        self.touch()

    def remove_metadata(self, key: str) -> None:
        """Remove a metadata entry."""
        self.metadata.pop(key, None)
        self.touch()

    def rename(self, title: str) -> None:
        """Rename the shot."""
        self.title = title.strip()
        self.touch()

    def clone_metadata(self) -> dict[str, Any]:
        """Return a shallow copy of the metadata dict."""
        return dict(self.metadata)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def character_count(self) -> int:
        """Number of character appearances in this shot."""
        return len(self.characters)

    @property
    def asset_count(self) -> int:
        """Number of generated assets linked to this shot."""
        return len(self.asset_ids)

    @property
    def generation_count(self) -> int:
        """Total number of generation attempts."""
        return self.generation_attempts

    @property
    def duration_frames(self) -> int:
        """
        Shot duration expressed in frames, using the render fps.
        BUG FIX: was using the now-removed Shot.fps field.
        Uses render.fps as the authoritative frame rate.
        """
        return round(self.duration_seconds * self.render.fps)

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def is_draft(self) -> bool:
        return self.status == ShotStatus.DRAFT

    @property
    def is_ready(self) -> bool:
        return self.status == ShotStatus.READY

    @property
    def is_generating(self) -> bool:
        return self.status == ShotStatus.GENERATING

    @property
    def is_review(self) -> bool:
        return self.status == ShotStatus.REVIEW

    @property
    def is_approved(self) -> bool:
        return self.status == ShotStatus.APPROVED

    @property
    def is_completed(self) -> bool:
        return self.status == ShotStatus.COMPLETED

    @property
    def has_assets(self) -> bool:
        return bool(self.asset_ids)

    @property
    def has_characters(self) -> bool:
        return bool(self.characters)

    @property
    def has_generation(self) -> bool:
        return self.generation_id is not None

    @property
    def has_image_prompt(self) -> bool:
        return bool(self.image_prompt)

    @property
    def has_video_prompt(self) -> bool:
        return bool(self.video_prompt)

    # BUG FIX: removed has_audio property that checked `self.audio is not None`.
    # audio is typed AudioSettings with a default_factory — it is NEVER None.
    # The old check was always True and gave false confidence. Replaced with
    # a semantically meaningful check against the AudioSettings content.
    @property
    def has_narration(self) -> bool:
        """True when narration text is present in the audio settings."""
        return self.audio.has_narration

    @property
    def has_music(self) -> bool:
        """True when background music is enabled."""
        return self.audio.has_music

    # ------------------------------------------------------------------
    # Prompt Helpers
    # ------------------------------------------------------------------

    def build_generation_prompt(self) -> str:
        """
        Assemble a complete AI generation prompt from all components.

        The prompt is built from the structured component fields.
        If an explicit image_prompt override is set it takes precedence.
        """
        if self.image_prompt:
            return self.image_prompt

        parts = [
            self.description,
            self.camera.prompt,
            self.lighting.prompt,
            self.environment.prompt,
            self.composition.prompt,
            self.visual_style.prompt,
            self.effects.prompt,
        ]

        # Append character appearance prompts
        for character in self.characters:
            if character.prompt:
                parts.append(character.prompt)

        # Filter empty strings and join
        return ", ".join(p for p in parts if p.strip())

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"Shot {self.shot_number}: {self.title}"

    def __repr__(self) -> str:
        return (
            "Shot("
            f"id={self.id}, "
            f"shot_number={self.shot_number}, "
            f"title={self.title!r}, "
            f"status={self.status.value!r}"
            ")"
        )
