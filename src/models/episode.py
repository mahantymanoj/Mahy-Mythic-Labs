"""
src/models/episode.py

Episode domain models.

An Episode is the primary production unit within a Project.

Hierarchy
---------
Project
    └── Episode
            ├── Research
            ├── Script
            ├── Storyboard
            ├── Scene
            ├── Shot
            ├── Generation
            └── Asset

Episode acts as the Aggregate Root for production.

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
# Enums
# ==============================================================================


class EpisodeStatus(str, Enum):
    """
    Episode lifecycle.
    """

    PLANNING = "planning"

    RESEARCH = "research"

    SCRIPTING = "scripting"

    STORYBOARDING = "storyboarding"

    PRODUCTION = "production"

    REVIEW = "review"

    COMPLETED = "completed"

    ARCHIVED = "archived"


# ==============================================================================
# Episode
# ==============================================================================


class Episode(EntityModel):
    """
    Represents one complete production episode.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    project_id: UUID = Field(
        description="Parent project."
    )

    research_id: UUID | None = None

    script_id: UUID | None = None

    storyboard_id: UUID | None = None

    scene_ids: list[UUID] = Field(
        default_factory=list,
    )

    shot_ids: list[UUID] = Field(
        default_factory=list,
    )

    generation_ids: list[UUID] = Field(
        default_factory=list,
    )

    asset_ids: list[UUID] = Field(
        default_factory=list,
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    episode_number: int = Field(
        ge=1,
    )

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    subtitle: str | None = None

    description: str | None = None

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status: EpisodeStatus = Field(
        default=EpisodeStatus.PLANNING,
    )

    published: bool = False

    # ------------------------------------------------------------------
    # Production
    # ------------------------------------------------------------------

    target_duration_minutes: float = Field(
        default=10.0,
        ge=1,
    )

    actual_duration_minutes: float | None = Field(
        default=None,
        ge=0,
    )

    target_language: str = Field(
        default="English",
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
    def validate_title(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Episode title cannot be empty."
            )

        return value

    # ------------------------------------------------------------------
    # Relationship Management
    # ------------------------------------------------------------------

    def set_research(
        self,
        research_id: UUID,
    ) -> None:
        """
        Associate a research document.
        """
        self.research_id = research_id
        self.touch()

    def set_script(
        self,
        script_id: UUID,
    ) -> None:
        """
        Associate a script.
        """
        self.script_id = script_id
        self.touch()

    def set_storyboard(
        self,
        storyboard_id: UUID,
    ) -> None:
        """
        Associate a storyboard.
        """
        self.storyboard_id = storyboard_id
        self.touch()

    # ------------------------------------------------------------------
    # Scene Management
    # ------------------------------------------------------------------

    def add_scene(
        self,
        scene_id: UUID,
    ) -> None:
        """
        Add a scene reference.
        """

        if scene_id not in self.scene_ids:
            self.scene_ids.append(scene_id)
            self.touch()

    def remove_scene(
        self,
        scene_id: UUID,
    ) -> None:
        """
        Remove a scene reference.
        """

        if scene_id in self.scene_ids:
            self.scene_ids.remove(scene_id)
            self.touch()

    # ------------------------------------------------------------------
    # Shot Management
    # ------------------------------------------------------------------

    def add_shot(
        self,
        shot_id: UUID,
    ) -> None:
        """
        Add a shot reference.
        """

        if shot_id not in self.shot_ids:
            self.shot_ids.append(shot_id)
            self.touch()

    def remove_shot(
        self,
        shot_id: UUID,
    ) -> None:
        """
        Remove a shot reference.
        """

        if shot_id in self.shot_ids:
            self.shot_ids.remove(shot_id)
            self.touch()

    # ------------------------------------------------------------------
    # Generation Management
    # ------------------------------------------------------------------

    def add_generation(
        self,
        generation_id: UUID,
    ) -> None:
        """
        Add a generation reference.
        """

        if generation_id not in self.generation_ids:
            self.generation_ids.append(generation_id)
            self.touch()

    def remove_generation(
        self,
        generation_id: UUID,
    ) -> None:
        """
        Remove a generation reference.
        """

        if generation_id in self.generation_ids:
            self.generation_ids.remove(generation_id)
            self.touch()

    # ------------------------------------------------------------------
    # Asset Management
    # ------------------------------------------------------------------

    def add_asset(
        self,
        asset_id: UUID,
    ) -> None:
        """
        Add an asset reference.
        """

        if asset_id not in self.asset_ids:
            self.asset_ids.append(asset_id)
            self.touch()

    def remove_asset(
        self,
        asset_id: UUID,
    ) -> None:
        """
        Remove an asset reference.
        """

        if asset_id in self.asset_ids:
            self.asset_ids.remove(asset_id)
            self.touch()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_research(self) -> None:
        """
        Move episode into research.
        """

        self.status = EpisodeStatus.RESEARCH
        self.touch()

    def start_scripting(self) -> None:
        """
        Move episode into scripting.
        """

        self.status = EpisodeStatus.SCRIPTING
        self.touch()

    def start_storyboarding(self) -> None:
        """
        Move episode into storyboarding.
        """

        self.status = EpisodeStatus.STORYBOARDING
        self.touch()

    def start_production(self) -> None:
        """
        Move episode into production.
        """

        self.status = EpisodeStatus.PRODUCTION
        self.touch()

    def submit_for_review(self) -> None:
        """
        Submit episode for review.
        """

        self.status = EpisodeStatus.REVIEW
        self.touch()

    def complete(self) -> None:
        """
        Mark episode as completed.
        """

        self.status = EpisodeStatus.COMPLETED
        self.touch()

    def archive(self) -> None:
        """
        Archive episode.
        """

        self.status = EpisodeStatus.ARCHIVED
        self.touch()


        # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def scene_count(self) -> int:
        """
        Total scenes.
        """
        return len(self.scene_ids)

    @property
    def shot_count(self) -> int:
        """
        Total shots.
        """
        return len(self.shot_ids)

    @property
    def generation_count(self) -> int:
        """
        Total AI generations.
        """
        return len(self.generation_ids)

    @property
    def asset_count(self) -> int:
        """
        Total generated assets.
        """
        return len(self.asset_ids)

    @property
    def completion_percentage(self) -> float:
        """
        Estimate production progress.
        """

        completed_steps = 0

        if self.research_id:
            completed_steps += 1

        if self.script_id:
            completed_steps += 1

        if self.storyboard_id:
            completed_steps += 1

        if self.scene_ids:
            completed_steps += 1

        if self.shot_ids:
            completed_steps += 1

        if self.generation_ids:
            completed_steps += 1

        if self.asset_ids:
            completed_steps += 1

        return round(
            completed_steps / 7 * 100,
            2,
        )

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def is_planning(self) -> bool:
        return self.status == EpisodeStatus.PLANNING

    @property
    def is_research(self) -> bool:
        return self.status == EpisodeStatus.RESEARCH

    @property
    def is_scripting(self) -> bool:
        return self.status == EpisodeStatus.SCRIPTING

    @property
    def is_storyboarding(self) -> bool:
        return self.status == EpisodeStatus.STORYBOARDING

    @property
    def is_production(self) -> bool:
        return self.status == EpisodeStatus.PRODUCTION

    @property
    def is_review(self) -> bool:
        return self.status == EpisodeStatus.REVIEW

    @property
    def is_completed(self) -> bool:
        return self.status == EpisodeStatus.COMPLETED

    @property
    def is_archived(self) -> bool:
        return self.status == EpisodeStatus.ARCHIVED

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
    # Utility Methods
    # ------------------------------------------------------------------

    def rename(
        self,
        title: str,
    ) -> None:
        """
        Rename episode.
        """

        self.title = title.strip()
        self.touch()

    def reset(self) -> None:
        """
        Reset production workflow.
        """

        self.status = EpisodeStatus.PLANNING
        self.published = False

        self.research_id = None
        self.script_id = None
        self.storyboard_id = None

        self.scene_ids.clear()
        self.shot_ids.clear()
        self.generation_ids.clear()
        self.asset_ids.clear()

        self.touch()

    def clone_metadata(self) -> dict[str, Any]:
        """
        Return a shallow copy of metadata.
        """

        return dict(self.metadata)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"Episode {self.episode_number}: "
            f"{self.title}"
        )

    def __repr__(self) -> str:
        return (
            "Episode("
            f"id={self.id}, "
            f"episode={self.episode_number}, "
            f"title={self.title!r}, "
            f"status={self.status.value!r}"
            ")"
        )