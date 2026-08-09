"""
src/models/components/reference.py

Reusable reference asset configuration for
Mahy Mythic Labs Studio OS.

A ReferenceAsset describes an existing asset that should be
used as a canonical visual, audio, stylistic, or contextual
reference during generation.

The actual asset/file belongs to the Asset domain model.

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


ReferenceType = Literal[
    "image",
    "video",
    "audio",
    "document",
    "prompt",
    "style",
    "character",
    "environment",
    "prop",
    "costume",
    "location",
    "other",
]


ReferencePurpose = Literal[
    "identity",
    "appearance",
    "face",
    "body",
    "costume",
    "pose",
    "environment",
    "lighting",
    "composition",
    "style",
    "voice",
    "motion",
    "prop",
    "continuity",
    "historical_accuracy",
    "mythological_accuracy",
    "other",
]


ReferenceSource = Literal[
    "generated",
    "uploaded",
    "researched",
    "official",
    "public_domain",
    "licensed",
    "internal",
    "unknown",
]


class ReferenceAsset(ValueModel):
    """
    Canonical reference to an existing Studio OS asset.

    This is a Value Object.

    The actual media belongs to Asset.
    ReferenceAsset describes how that media should be
    used by the generation and continuity systems.

    Examples
    --------
    A canonical image of Lord Shiva's appearance.

    A historical painting used as a visual reference.

    A voice sample used to maintain character voice consistency.

    A costume image used for continuity across scenes.
    """

    # ------------------------------------------------------------------
    # Asset Reference
    # ------------------------------------------------------------------

    asset_id: str = Field(
        ...,
        min_length=1,
        description="ID of the referenced Asset.",
    )

    asset_version: str | None = Field(
        default=None,
        description="Specific asset version to use.",
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    reference_type: ReferenceType = Field(
        ...,
        description="Type of reference asset.",
    )

    purpose: ReferencePurpose = Field(
        ...,
        description="Reason this reference is used.",
    )

    source: ReferenceSource = Field(
        default="internal",
        description="Origin of the reference asset.",
    )

    # ------------------------------------------------------------------
    # Authority
    # ------------------------------------------------------------------

    canonical: bool = Field(
        default=True,
        description=(
            "Whether this reference represents the canonical "
            "appearance or source of truth."
        ),
    )

    approved: bool = Field(
        default=False,
        description="Whether the reference has passed review.",
    )

    priority: int = Field(
        default=1,
        ge=1,
        le=100,
        description=(
            "Reference priority. Lower values have higher priority."
        ),
    )

    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description=(
            "Relative influence of this reference during generation."
        ),
    )

    # ------------------------------------------------------------------
    # Generation Context
    # ------------------------------------------------------------------

    tags: list[str] = Field(
        default_factory=list,
        description="Searchable reference tags.",
    )

    prompt_hints: list[str] = Field(
        default_factory=list,
        description=(
            "Prompt instructions derived from this reference."
        ),
    )

    negative_hints: list[str] = Field(
        default_factory=list,
        description=(
            "Visual characteristics that should not be introduced."
        ),
    )

    # ------------------------------------------------------------------
    # Continuity
    # ------------------------------------------------------------------

    valid_from_episode_id: str | None = Field(
        default=None,
        description="First episode where this reference is valid.",
    )

    valid_until_episode_id: str | None = Field(
        default=None,
        description="Last episode where this reference is valid.",
    )

    continuity_notes: str | None = Field(
        default=None,
        description="Continuity instructions for this reference.",
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    description: str | None = Field(
        default=None,
        description="Human-readable reference description.",
    )

    notes: str | None = Field(
        default=None,
        description="Additional internal notes.",
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Additional provider-independent metadata.",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @field_validator("asset_id")
    @classmethod
    def validate_asset_id(cls, value: str) -> str:
        """Ensure the asset ID is not blank."""
        value = value.strip()

        if not value:
            raise ValueError(
                "asset_id cannot be empty."
            )

        return value

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_canonical(self) -> bool:
        """Return True when this is a canonical reference."""
        return self.canonical

    @property
    def is_approved(self) -> bool:
        """Return True when the reference has been approved."""
        return self.approved

    @property
    def is_high_priority(self) -> bool:
        """Return True for high-priority references."""
        return self.priority <= 10

    @property
    def is_visual(self) -> bool:
        """Return True when the reference is visual."""
        return self.reference_type in {
            "image",
            "video",
            "character",
            "environment",
            "prop",
            "costume",
            "location",
        }

    @property
    def is_audio(self) -> bool:
        """Return True when the reference contains audio."""
        return self.reference_type == "audio"

    @property
    def is_historical(self) -> bool:
        """Return True when used for historical accuracy."""
        return self.purpose == "historical_accuracy"

    @property
    def is_mythological(self) -> bool:
        """Return True when used for mythological accuracy."""
        return self.purpose == "mythological_accuracy"

    # ------------------------------------------------------------------
    # Prompt Generation
    # ------------------------------------------------------------------

    @property
    def prompt(self) -> str:
        """
        Build a reusable reference prompt fragment.
        """

        parts = [
            f"{self.reference_type} reference",
            f"purpose: {self.purpose}",
        ]

        if self.canonical:
            parts.append("canonical reference")

        if self.approved:
            parts.append("approved reference")

        if self.prompt_hints:
            parts.append(
                "preserve: "
                + ", ".join(self.prompt_hints)
            )

        if self.negative_hints:
            parts.append(
                "avoid: "
                + ", ".join(self.negative_hints)
            )

        if self.continuity_notes:
            parts.append(
                f"continuity: {self.continuity_notes}"
            )

        return ", ".join(parts)