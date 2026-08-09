"""
src/models/components/personality.py

Reusable personality profile for Mahy Mythic Labs Studio OS.

This module defines the behavioural characteristics of a character.
It intentionally contains no appearance or identity information.

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


Temperament = Literal[
    "calm",
    "balanced",
    "energetic",
    "aggressive",
    "patient",
    "reserved",
    "compassionate",
]

Archetype = Literal[
    "hero",
    "mentor",
    "leader",
    "scholar",
    "guardian",
    "explorer",
    "strategist",
    "creator",
    "healer",
    "sage",
    "villain",
]

SpeechStyle = Literal[
    "formal",
    "conversational",
    "storytelling",
    "poetic",
    "philosophical",
    "scientific",
]

DecisionStyle = Literal[
    "logical",
    "emotional",
    "balanced",
    "strategic",
    "intuitive",
]

HumorStyle = Literal[
    "none",
    "subtle",
    "playful",
    "sarcastic",
    "witty",
]

LeadershipStyle = Literal[
    "none",
    "servant",
    "authoritative",
    "inspirational",
    "democratic",
]


class PersonalityProfile(ValueModel):
    """
    Reusable behavioural profile.

    Shared by

    - Character
    - Dialogue generation
    - Narration
    - Master Director
    """

    temperament: Temperament = Field(
        default="balanced",
        description="Overall temperament.",
    )

    archetype: Archetype = Field(
        default="hero",
        description="Narrative archetype.",
    )

    speech_style: SpeechStyle = Field(
        default="formal",
        description="Preferred speaking style.",
    )

    decision_style: DecisionStyle = Field(
        default="balanced",
        description="How decisions are typically made.",
    )

    humor_style: HumorStyle = Field(
        default="none",
        description="Sense of humor.",
    )

    leadership_style: LeadershipStyle = Field(
        default="none",
        description="Leadership approach.",
    )

    intelligence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Analytical capability.",
    )

    wisdom: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Practical and philosophical wisdom.",
    )

    courage: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Bravery under pressure.",
    )

    compassion: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Empathy toward others.",
    )

    patience: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Ability to remain calm over time.",
    )

    curiosity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Desire to learn and explore.",
    )

    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Self-confidence.",
    )

    emotional_control: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Control over emotions.",
    )

    strengths: list[str] = Field(
        default_factory=list,
        description="Key strengths.",
    )

    weaknesses: list[str] = Field(
        default_factory=list,
        description="Known weaknesses.",
    )

    motivations: list[str] = Field(
        default_factory=list,
        description="Primary motivations.",
    )

    fears: list[str] = Field(
        default_factory=list,
        description="Primary fears or concerns.",
    )

    values: list[str] = Field(
        default_factory=list,
        description="Core values and beliefs.",
    )

    favorite_phrases: list[str] = Field(
        default_factory=list,
        description="Frequently used phrases.",
    )

    behavioral_rules: list[str] = Field(
        default_factory=list,
        description="Rules the character consistently follows.",
    )

    prohibited_behaviors: list[str] = Field(
        default_factory=list,
        description="Behaviors the character should avoid.",
    )

    notes: str | None = Field(
        default=None,
        description="Additional personality notes.",
    )

    @property
    def is_leader(self) -> bool:
        """Return True if the character has a leadership role."""
        return self.leadership_style != "none"

    @property
    def is_philosophical(self) -> bool:
        """Return True when philosophical speech is preferred."""
        return self.speech_style == "philosophical"

    @property
    def is_highly_intelligent(self) -> bool:
        """Return True when intelligence is very high."""
        return self.intelligence >= 0.9

    @property
    def prompt(self) -> str:
        """
        Build a reusable personality prompt fragment.
        """
        parts = [
            self.temperament,
            self.archetype,
            self.speech_style,
            self.decision_style,
        ]

        if self.values:
            parts.append(
                "values: " + ", ".join(self.values)
            )

        if self.behavioral_rules:
            parts.append(
                "behavior: " + ", ".join(self.behavioral_rules)
            )

        return ", ".join(parts)