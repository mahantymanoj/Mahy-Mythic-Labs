"""
src/models/project.py

Project domain model.

A Project is the highest-level aggregate in Studio OS.

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


class ProjectStatus(str, Enum):
    """
    Project lifecycle.
    """

    PLANNING = "planning"

    ACTIVE = "active"

    REVIEW = "review"

    COMPLETED = "completed"

    ARCHIVED = "archived"


# ==============================================================================
# Project
# ==============================================================================


class Project(EntityModel):
    """
    Represents one production project.
    """

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    owner: str | None = None

    # ------------------------------------------------------------------
    # Production
    # ------------------------------------------------------------------

    status: ProjectStatus = Field(
        default=ProjectStatus.PLANNING,
    )

    target_language: str = Field(
        default="English",
    )

    genre: str | None = None

    series_name: str | None = None

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    episode_ids: list[UUID] = Field(
        default_factory=list,
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

    @field_validator("name")
    @classmethod
    def validate_name(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Project name cannot be empty."
            )

        return value

        # ------------------------------------------------------------------
    # Episode Management
    # ------------------------------------------------------------------

    def add_episode(
        self,
        episode_id: UUID,
    ) -> None:
        """
        Add an episode to the project.
        """

        if episode_id not in self.episode_ids:
            self.episode_ids.append(episode_id)
            self.touch()

    def remove_episode(
        self,
        episode_id: UUID,
    ) -> None:
        """
        Remove an episode from the project.
        """

        if episode_id in self.episode_ids:
            self.episode_ids.remove(episode_id)
            self.touch()

    def has_episode(
        self,
        episode_id: UUID,
    ) -> bool:
        """
        Check whether an episode belongs to the project.
        """

        return episode_id in self.episode_ids

    def clear_episodes(self) -> None:
        """
        Remove every episode reference.
        """

        self.episode_ids.clear()
        self.touch()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def activate(self) -> None:
        """
        Start project execution.
        """

        self.status = ProjectStatus.ACTIVE
        self.touch()

    def submit_for_review(self) -> None:
        """
        Move project into review.
        """

        self.status = ProjectStatus.REVIEW
        self.touch()

    def complete(self) -> None:
        """
        Mark project as completed.
        """

        self.status = ProjectStatus.COMPLETED
        self.touch()

    def archive(self) -> None:
        """
        Archive the project.
        """

        self.status = ProjectStatus.ARCHIVED
        self.touch()

    def reset(self) -> None:
        """
        Reset project back to planning.
        """

        self.status = ProjectStatus.PLANNING
        self.touch()

        # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def episode_count(self) -> int:
        """
        Total number of episodes.
        """
        return len(self.episode_ids)

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def is_planning(self) -> bool:
        return self.status == ProjectStatus.PLANNING

    @property
    def is_active(self) -> bool:
        return self.status == ProjectStatus.ACTIVE

    @property
    def is_review(self) -> bool:
        return self.status == ProjectStatus.REVIEW

    @property
    def is_completed(self) -> bool:
        return self.status == ProjectStatus.COMPLETED

    @property
    def is_archived(self) -> bool:
        return self.status == ProjectStatus.ARCHIVED

    @property
    def has_episodes(self) -> bool:
        """
        Whether the project contains any episodes.
        """
        return bool(self.episode_ids)

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
        Remove metadata.
        """

        self.metadata.pop(key, None)
        self.touch()

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def rename(
        self,
        name: str,
    ) -> None:
        """
        Rename the project.
        """

        self.name = name.strip()
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
        return self.name

    def __repr__(self) -> str:
        return (
            "Project("
            f"id={self.id}, "
            f"name={self.name!r}, "
            f"episodes={self.episode_count}, "
            f"status={self.status.value!r}"
            ")"
        )