"""
src/models/components/character_appearance.py

Reusable character appearance configuration for
Mahy Mythic Labs Studio OS.

This module defines the visual appearance of a character.
It intentionally contains no identity information such as
name or biography. Those belong to the Character entity.

Author
------
Mahy Mythic Labs

Python
------
>=3.11
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from src.models.base import ValueModel


Gender = Literal[
    "male",
    "female",
    "non_binary",
    "unknown",
]

BodyType = Literal[
    "slim",
    "athletic",
    "average",
    "muscular",
    "heavy",
]

HairLength = Literal[
    "bald",
    "short",
    "medium",
    "long",
    "very_long",
]

HairTexture = Literal[
    "straight",
    "wavy",
    "curly",
    "coily",
    "matted",
]

BeardStyle = Literal[
    "none",
    "stubble",
    "short",
    "medium",
    "long",
    "full",
]

Expression = Literal[
    "neutral",
    "happy",
    "sad",
    "angry",
    "calm",
    "focused",
    "divine",
    "mysterious",
]

Pose = Literal[
    "standing",
    "walking",
    "running",
    "sitting",
    "kneeling",
    "meditating",
    "flying",
]

EyeDirection = Literal[
    "camera",
    "left",
    "right",
    "up",
    "down",
]


class CharacterAppearance(ValueModel):
    """
    Reusable appearance definition.

    Shared by

    - Character
    - Shot
    - Storyboard
    - Image Generation
    """

    age_appearance: int = Field(
        default=30,
        ge=0,
        le=120,
    )

    gender: Gender = Field(
        default="unknown",
    )

    body_type: BodyType = Field(
        default="average",
    )

    height_cm: float | None = Field(
        default=None,
        ge=30,
        le=300,
    )

    weight_kg: float | None = Field(
        default=None,
        ge=1,
        le=500,
    )

    skin_tone: str = Field(
        default="medium",
    )

    hair_color: str = Field(
        default="black",
    )

    hair_length: HairLength = Field(
        default="medium",
    )

    hair_texture: HairTexture = Field(
        default="straight",
    )

    eye_color: str = Field(
        default="brown",
    )

    beard_style: BeardStyle = Field(
        default="none",
    )

    facial_features: list[str] = Field(
        default_factory=list,
        description="Distinct facial features.",
    )

    clothing: str = Field(
        default="",
        description="Primary clothing description.",
    )

    accessories: list[str] = Field(
        default_factory=list,
        description="Jewelry, weapons, ornaments, etc.",
    )

    expression: Expression = Field(
        default="neutral",
    )

    pose: Pose = Field(
        default="standing",
    )

    eye_direction: EyeDirection = Field(
        default="camera",
    )

    tattoos: list[str] = Field(
        default_factory=list,
    )

    scars: list[str] = Field(
        default_factory=list,
    )

    markings: list[str] = Field(
        default_factory=list,
        description="Tilak, ash, divine marks, etc.",
    )

    dominant_hand: Literal[
        "left",
        "right",
        "ambidextrous",
    ] = Field(
        default="right",
    )

    custom_attributes: dict[str, str] = Field(
        default_factory=dict,
        description="Provider-independent appearance extensions.",
    )

    @property
    def has_beard(self) -> bool:
        """Return True if a beard is present."""
        return self.beard_style != "none"

    @property
    def has_accessories(self) -> bool:
        """Return True if accessories exist."""
        return len(self.accessories) > 0

    @property
    def has_markings(self) -> bool:
        """Return True if body or face markings exist."""
        return len(self.markings) > 0

    @property
    def prompt(self) -> str:
        """
        Build a reusable appearance prompt fragment.
        """
        parts = [
            f"{self.age_appearance} years old appearance",
            self.gender.replace("_", " "),
            self.body_type,
            f"{self.skin_tone} skin",
            f"{self.hair_length.replace('_', ' ')} {self.hair_color} hair",
            f"{self.eye_color} eyes",
            self.expression,
            self.pose,
        ]

        if self.clothing:
            parts.append(self.clothing)

        parts.extend(self.accessories)
        parts.extend(self.markings)
        parts.extend(self.facial_features)

        return ", ".join(parts)