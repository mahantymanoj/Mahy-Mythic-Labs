"""
src/models/storyboard.py

Storyboard domain models.

A Storyboard represents the visual planning of an Episode before
AI generation begins.

Hierarchy
---------
Project
    └── Episode
            └── Storyboard
                    └── StoryboardPage
                            └── StoryboardFrame

IMPORTANT: StoryboardFrame is defined BEFORE StoryboardPage
           so that StoryboardPage can reference it without
           forward-reference resolution issues.

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
from uuid import UUID

from pydantic import Field, field_validator

from .base import EntityModel, ValueModel


# ==============================================================================
# Enums
# ==============================================================================


class StoryboardStatus(str, Enum):
    """Storyboard lifecycle."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    LOCKED = "locked"
    ARCHIVED = "archived"


class StoryboardFrameType(str, Enum):
    """Frame type."""

    ESTABLISHING = "establishing"
    ACTION = "action"
    DIALOGUE = "dialogue"
    CLOSE_UP = "close_up"
    CUTAWAY = "cutaway"
    TRANSITION = "transition"
    EFFECT = "effect"
    ENDING = "ending"


# ==============================================================================
# StoryboardFrame — defined BEFORE StoryboardPage uses it
# ==============================================================================


class StoryboardFrame(ValueModel):
    """
    A single storyboard frame describing one shot.
    Immutable value object — compared by value.
    """

    frame_number: int = Field(
        ge=1,
        description="Frame order within the page.",
    )

    frame_type: StoryboardFrameType = Field(
        default=StoryboardFrameType.ACTION,
    )

    scene_id: Optional[UUID] = Field(
        default=None,
        description="Referenced scene UUID.",
    )

    shot_id: Optional[UUID] = Field(
        default=None,
        description="Referenced shot UUID.",
    )

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str = Field(
        default="",
        description="Visual description of this frame.",
    )

    narration: Optional[str] = Field(
        default=None,
        description="Narration text synced to this frame.",
    )

    camera_direction: Optional[str] = Field(
        default=None,
        description="Camera movement / angle direction.",
    )

    duration_seconds: float = Field(
        default=5.0,
        gt=0,
        description="Planned shot duration.",
    )

    approved: bool = Field(
        default=False,
        description="Whether this frame has been approved.",
    )

    image_uri: Optional[str] = Field(
        default=None,
        description="Generated or reference image URI.",
    )

    notes: Optional[str] = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Frame title cannot be empty.")
        return value

    def __str__(self) -> str:
        return f"Frame {self.frame_number}: {self.title}"

    def __repr__(self) -> str:
        return (
            "StoryboardFrame("
            f"frame_number={self.frame_number}, "
            f"type={self.frame_type.value!r}, "
            f"approved={self.approved}"
            ")"
        )


# ==============================================================================
# StoryboardPage — uses StoryboardFrame (defined above)
# ==============================================================================


class StoryboardPage(ValueModel):
    """
    Represents one storyboard page.
    A page contains one or more storyboard frames.
    Immutable value object — compared by value.
    """

    page_number: int = Field(
        ge=1,
        description="Storyboard page number.",
    )

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: Optional[str] = Field(default=None)

    frames: List[StoryboardFrame] = Field(
        default_factory=list,
        description="Storyboard frames.",
    )

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
            raise ValueError("Page title cannot be empty.")
        return value

    # ------------------------------------------------------------------
    # Frame Management
    # ------------------------------------------------------------------

    def add_frame(self, frame: StoryboardFrame) -> "StoryboardPage":
        """Return a new page with an additional frame."""
        return self.replace(frames=[*self.frames, frame])

    def remove_frame(self, frame_number: int) -> "StoryboardPage":
        """Return a new page without the specified frame."""
        return self.replace(
            frames=[f for f in self.frames if f.frame_number != frame_number]
        )

    def update_frame(self, frame: StoryboardFrame) -> "StoryboardPage":
        """Replace an existing frame matched by frame_number."""
        updated: List[StoryboardFrame] = []
        replaced = False
        for existing in self.frames:
            if existing.frame_number == frame.frame_number:
                updated.append(frame)
                replaced = True
            else:
                updated.append(existing)
        if not replaced:
            updated.append(frame)
        return self.replace(frames=updated)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def approved_frames(self) -> int:
        return sum(1 for f in self.frames if f.approved)

    @property
    def completion_percentage(self) -> float:
        if not self.frames:
            return 0.0
        return round(self.approved_frames / len(self.frames) * 100, 2)

    def __str__(self) -> str:
        return f"Storyboard Page {self.page_number}"

    def __repr__(self) -> str:
        return (
            "StoryboardPage("
            f"page_number={self.page_number}, "
            f"frames={self.frame_count}"
            ")"
        )


# ==============================================================================
# Storyboard Entity — owns identity and lifecycle
# ==============================================================================


class Storyboard(EntityModel):
    """
    Represents the storyboard for an episode.

    Uses EntityModel because storyboards have persistent identity
    and are tracked through review and approval workflows.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    project_id: UUID = Field(description="Associated project.")
    episode_id: UUID = Field(description="Associated episode.")

    scene_ids: List[UUID] = Field(default_factory=list)
    shot_ids: List[UUID] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    version_name: str = Field(default="v1")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status: StoryboardStatus = Field(default=StoryboardStatus.DRAFT)
    approved: bool = False
    locked: bool = False

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    pages: List[StoryboardPage] = Field(default_factory=list)
    notes: Optional[str] = None
    review_notes: Optional[str] = None

    # ------------------------------------------------------------------
    # Production
    # ------------------------------------------------------------------

    estimated_duration_seconds: float = Field(default=0.0, ge=0)
    actual_duration_seconds: Optional[float] = Field(default=None, ge=0)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    tags: List[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Storyboard title cannot be empty.")
        return value

    # ------------------------------------------------------------------
    # Page Management
    # ------------------------------------------------------------------

    def add_page(self, page: StoryboardPage) -> None:
        self.pages.append(page)
        self.touch()

    def remove_page(self, page_number: int) -> None:
        self.pages = [p for p in self.pages if p.page_number != page_number]
        self.touch()

    def clear_pages(self) -> None:
        self.pages.clear()
        self.touch()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def submit_for_review(self) -> None:
        self.status = StoryboardStatus.REVIEW
        self.touch()

    def approve(self) -> None:
        self.status = StoryboardStatus.APPROVED
        self.approved = True
        self.touch()

    def lock(self) -> None:
        self.status = StoryboardStatus.LOCKED
        self.locked = True
        self.touch()

    def archive(self) -> None:
        self.status = StoryboardStatus.ARCHIVED
        self.touch()

    def reset_review(self) -> None:
        self.status = StoryboardStatus.DRAFT
        self.approved = False
        self.locked = False
        self.review_notes = None
        self.touch()

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def frame_count(self) -> int:
        return sum(p.frame_count for p in self.pages)

    @property
    def approved_frame_count(self) -> int:
        return sum(p.approved_frames for p in self.pages)

    @property
    def completion_percentage(self) -> float:
        if self.frame_count == 0:
            return 0.0
        return round((self.approved_frame_count / self.frame_count) * 100, 2)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_draft(self) -> bool:
        return self.status == StoryboardStatus.DRAFT

    @property
    def is_approved(self) -> bool:
        return self.status == StoryboardStatus.APPROVED

    @property
    def is_locked(self) -> bool:
        return self.status == StoryboardStatus.LOCKED

    # ------------------------------------------------------------------
    # Metadata Helpers
    # ------------------------------------------------------------------

    def add_tag(self, tag: str) -> None:
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.touch()

    def update_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
        self.touch()

    def rename(self, title: str) -> None:
        self.title = title.strip()
        self.touch()

    def clone_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            "Storyboard("
            f"id={self.id}, "
            f"title={self.title!r}, "
            f"pages={self.page_count}, "
            f"frames={self.frame_count}, "
            f"status={self.status.value!r}"
            ")"
        )
