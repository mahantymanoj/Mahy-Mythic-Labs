"""
src/models/components/continuity.py

Reusable continuity configuration for Mahy Mythic Labs Studio OS.

This module defines continuity requirements and constraints that
the Master Director can use when generating shots and scenes.

Continuity history itself should be maintained by the higher-level
continuity/episode/project systems.

Author
------
Mahy Mythic Labs

Python
------
>=3.11
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from src.models.base import ValueModel


ContinuityLevel = Literal[
    "none",
    "low",
    "medium",
    "high",
    "strict",
]

ContinuityType = Literal[
    "character",
    "appearance",
    "costume",
    "prop",
    "location",
    "environment",
    "lighting",
    "camera",
    "composition",
    "visual_style",
    "voice",
    "audio",
    "story",
    "timeline",
]

ChangePolicy = Literal[
    "allow",
    "prefer_consistency",
    "require_approval",
    "forbid",
]


class ContinuityRule(ValueModel):
    """
    A single continuity constraint.

    Example
    -------
    Keep Shiva's trident identical across all shots.
    """

    continuity_type: ContinuityType = Field(
        ...,
        description="Category governed by this rule.",
    )

    name: str = Field(
        ...,
        min_length=1,
        description="Human-readable rule name.",
    )

    description: str = Field(
        ...,
        min_length=1,
        description="Continuity requirement.",
    )

    policy: ChangePolicy = Field(
        default="prefer_consistency",
        description="How changes should be handled.",
    )

    priority: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Rule priority. Higher values are more important.",
    )

    source_reference_ids: list[str] = Field(
        default_factory=list,
        description="Reference IDs supporting this rule.",
    )

    @field_validator("name", "description")
    @classmethod
    def validate_text(cls, value: str) -> str:
        """Normalize rule text."""
        value = value.strip()

        if not value:
            raise ValueError(
                "Continuity rule text cannot be empty."
            )

        return value

    @property
    def is_strict(self) -> bool:
        """Return True when changes are forbidden."""
        return self.policy == "forbid"

    @property
    def requires_approval(self) -> bool:
        """Return True when changes require approval."""
        return self.policy == "require_approval"


class ContinuitySettings(ValueModel):
    """
    Continuity configuration for a shot, scene, or episode.

    This model describes what must remain consistent.

    It does NOT store the historical state of the project.

    Shared by

    - Shot
    - Scene
    - Storyboard
    - Episode
    - Master Director
    """

    # ------------------------------------------------------------------
    # Overall Configuration
    # ------------------------------------------------------------------

    level: ContinuityLevel = Field(
        default="high",
        description="Overall continuity strictness.",
    )

    enabled: bool = Field(
        default=True,
        description="Whether continuity enforcement is enabled.",
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    character_ids: list[str] = Field(
        default_factory=list,
        description="Characters whose continuity must be preserved.",
    )

    reference_asset_ids: list[str] = Field(
        default_factory=list,
        description="Canonical references to use.",
    )

    # ------------------------------------------------------------------
    # Continuity Flags
    # ------------------------------------------------------------------

    preserve_character_appearance: bool = Field(
        default=True,
        description="Preserve character appearance.",
    )

    preserve_costume: bool = Field(
        default=True,
        description="Preserve costume and clothing.",
    )

    preserve_props: bool = Field(
        default=True,
        description="Preserve important props.",
    )

    preserve_environment: bool = Field(
        default=True,
        description="Preserve environment details.",
    )

    preserve_lighting: bool = Field(
        default=True,
        description="Preserve lighting style.",
    )

    preserve_camera_language: bool = Field(
        default=True,
        description="Maintain established camera language.",
    )

    preserve_visual_style: bool = Field(
        default=True,
        description="Maintain established visual style.",
    )

    preserve_voice: bool = Field(
        default=True,
        description="Maintain character voice consistency.",
    )

    preserve_story_logic: bool = Field(
        default=True,
        description="Prevent contradictions in story continuity.",
    )

    preserve_timeline: bool = Field(
        default=True,
        description="Preserve chronological consistency.",
    )

    # ------------------------------------------------------------------
    # Scene State
    # ------------------------------------------------------------------

    previous_shot_id: str | None = Field(
        default=None,
        description="Immediately preceding shot.",
    )

    next_shot_id: str | None = Field(
        default=None,
        description="Immediately following shot.",
    )

    previous_scene_id: str | None = Field(
        default=None,
        description="Immediately preceding scene.",
    )

    continuity_anchor_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Shots or scenes that should be used as visual "
            "continuity anchors."
        ),
    )

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    rules: list[ContinuityRule] = Field(
        default_factory=list,
        description="Explicit continuity rules.",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @field_validator("character_ids", "reference_asset_ids")
    @classmethod
    def remove_blank_ids(
        cls,
        values: list[str],
    ) -> list[str]:
        """Remove empty IDs and normalize whitespace."""
        return [
            value.strip()
            for value in values
            if value.strip()
        ]

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_strict(self) -> bool:
        """Return True when strict continuity is required."""
        return self.level == "strict"

    @property
    def has_characters(self) -> bool:
        """Return True when characters are being tracked."""
        return bool(self.character_ids)

    @property
    def has_references(self) -> bool:
        """Return True when canonical references exist."""
        return bool(self.reference_asset_ids)

    @property
    def has_rules(self) -> bool:
        """Return True when explicit rules exist."""
        return bool(self.rules)

    @property
    def requires_continuity_check(self) -> bool:
        """
        Return True when the Master Director should perform
        a continuity validation before generation.
        """
        return (
            self.enabled
            and self.level in {
                "medium",
                "high",
                "strict",
            }
        )

    # ------------------------------------------------------------------
    # Rule Helpers
    # ------------------------------------------------------------------

    def rules_for(
        self,
        continuity_type: ContinuityType,
    ) -> list[ContinuityRule]:
        """
        Return rules belonging to a specific continuity category.
        """
        return [
            rule
            for rule in self.rules
            if rule.continuity_type == continuity_type
        ]

    def strict_rules(self) -> list[ContinuityRule]:
        """Return rules that forbid changes."""
        return [
            rule
            for rule in self.rules
            if rule.is_strict
        ]

    # ------------------------------------------------------------------
    # Prompt Generation
    # ------------------------------------------------------------------

    @property
    def prompt(self) -> str:
        """
        Build a reusable continuity prompt fragment.
        """

        if not self.enabled:
            return ""

        parts = [
            f"{self.level} continuity",
        ]

        if self.preserve_character_appearance:
            parts.append("preserve character appearance")

        if self.preserve_costume:
            parts.append("preserve costume")

        if self.preserve_props:
            parts.append("preserve props")

        if self.preserve_environment:
            parts.append("preserve environment")

        if self.preserve_lighting:
            parts.append("preserve lighting")

        if self.preserve_camera_language:
            parts.append("preserve camera language")

        if self.preserve_visual_style:
            parts.append("preserve visual style")

        if self.preserve_voice:
            parts.append("preserve voice")

        if self.preserve_story_logic:
            parts.append("preserve story continuity")

        if self.preserve_timeline:
            parts.append("preserve timeline")

        return ", ".join(parts)