"""
src/models/components/relationship.py

Reusable character relationship model for Mahy Mythic Labs Studio OS.

This module defines relationships between characters while keeping
the model independent of any specific mythology, historical period,
or AI provider.

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


RelationshipType = Literal[
    "parent",
    "child",
    "sibling",
    "spouse",
    "partner",
    "friend",
    "ally",
    "mentor",
    "student",
    "teacher",
    "disciple",
    "leader",
    "follower",
    "king",
    "subject",
    "rival",
    "enemy",
    "companion",
    "colleague",
    "ancestor",
    "descendant",
    "deity",
    "devotee",
    "creator",
    "creation",
    "other",
]


RelationshipStatus = Literal[
    "active",
    "inactive",
    "historical",
    "unknown",
]


class CharacterRelationship(ValueModel):
    """
    Describes a relationship between two characters.

    This is a Value Object.

    The Character entity owns the relationship.
    This model only describes the relationship itself.

    Examples
    --------
    Krishna -> Arjuna
        mentor

    Shiva -> Parvati
        spouse

    Einstein -> Newton
        intellectual influence / other
    """

    # ------------------------------------------------------------------
    # Identity References
    # ------------------------------------------------------------------

    target_character_id: str = Field(
        ...,
        min_length=1,
        description="ID of the related character.",
    )

    target_character_name: str | None = Field(
        default=None,
        description="Human-readable name of the related character.",
    )

    # ------------------------------------------------------------------
    # Relationship
    # ------------------------------------------------------------------

    relationship_type: RelationshipType = Field(
        ...,
        description="Primary relationship type.",
    )

    reciprocal_type: RelationshipType | None = Field(
        default=None,
        description=(
            "Relationship type from the target character's perspective."
        ),
    )

    status: RelationshipStatus = Field(
        default="active",
        description="Current status of the relationship.",
    )

    strength: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Strength of the relationship.",
    )

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Narrative importance of the relationship.",
    )

    # ------------------------------------------------------------------
    # Canon
    # ------------------------------------------------------------------

    canonical: bool = Field(
        default=True,
        description=(
            "Whether this relationship is supported by the project's "
            "canonical source material."
        ),
    )

    source_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Research/source IDs supporting this relationship."
        ),
    )

    # ------------------------------------------------------------------
    # Story Context
    # ------------------------------------------------------------------

    description: str | None = Field(
        default=None,
        description="Human-readable relationship description.",
    )

    first_episode_id: str | None = Field(
        default=None,
        description="Episode where the relationship first appears.",
    )

    last_episode_id: str | None = Field(
        default=None,
        description="Most recent episode where the relationship appears.",
    )

    interaction_rules: list[str] = Field(
        default_factory=list,
        description=(
            "Rules the Master Director should follow when these "
            "characters interact."
        ),
    )

    prohibited_interactions: list[str] = Field(
        default_factory=list,
        description=(
            "Interactions that should not occur because they violate "
            "character or canonical continuity."
        ),
    )

    notes: str | None = Field(
        default=None,
        description="Additional relationship notes.",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @field_validator("target_character_id")
    @classmethod
    def validate_target_character_id(cls, value: str) -> str:
        """Ensure character IDs are not blank."""
        value = value.strip()

        if not value:
            raise ValueError(
                "target_character_id cannot be empty."
            )

        return value

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_canonical(self) -> bool:
        """Return True when the relationship is canonical."""
        return self.canonical

    @property
    def is_strong(self) -> bool:
        """Return True when the relationship is strongly established."""
        return self.strength >= 0.75

    @property
    def is_narratively_important(self) -> bool:
        """Return True when the relationship is important to the story."""
        return self.importance >= 0.75

    @property
    def has_interaction_rules(self) -> bool:
        """Return True when interaction rules exist."""
        return bool(self.interaction_rules)

    # ------------------------------------------------------------------
    # Prompt Generation
    # ------------------------------------------------------------------

    @property
    def prompt(self) -> str:
        """
        Build a reusable relationship prompt fragment.
        """

        target = (
            self.target_character_name
            or self.target_character_id
        )

        parts = [
            f"relationship with {target}:",
            self.relationship_type,
        ]

        if self.reciprocal_type:
            parts.append(
                f"reciprocal role: {self.reciprocal_type}"
            )

        if self.description:
            parts.append(self.description)

        if self.interaction_rules:
            parts.append(
                "interaction rules: "
                + "; ".join(self.interaction_rules)
            )

        return ", ".join(parts)