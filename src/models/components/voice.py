"""
src/models/components/voice.py

Reusable voice configuration for Mahy Mythic Labs Studio OS.

This module defines the canonical voice characteristics of a
character or narrator. It is intentionally provider-independent.

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


VoiceGender = Literal[
    "male",
    "female",
    "neutral",
]

VoiceAge = Literal[
    "child",
    "teen",
    "young_adult",
    "adult",
    "middle_aged",
    "elder",
]

VoiceTone = Literal[
    "calm",
    "warm",
    "deep",
    "soft",
    "authoritative",
    "mysterious",
    "divine",
    "heroic",
    "villainous",
    "narrator",
]

SpeechStyle = Literal[
    "formal",
    "conversational",
    "storytelling",
    "documentary",
    "cinematic",
    "poetic",
]

Accent = Literal[
    "neutral",
    "indian",
    "british",
    "american",
    "ancient_indian",
]


class VoiceSettings(ValueModel):
    """
    Provider-independent voice definition.

    Shared by

    - Character
    - Narrator
    - AudioSettings
    """

    voice_name: str = Field(
        default="Default",
        description="Human-friendly voice name.",
    )

    language: str = Field(
        default="en",
        description="Primary language code (ISO 639-1).",
    )

    accent: Accent = Field(
        default="neutral",
        description="Preferred accent.",
    )

    gender: VoiceGender = Field(
        default="neutral",
        description="Voice gender.",
    )

    age: VoiceAge = Field(
        default="adult",
        description="Perceived voice age.",
    )

    tone: VoiceTone = Field(
        default="calm",
        description="Overall vocal tone.",
    )

    speech_style: SpeechStyle = Field(
        default="storytelling",
        description="Speaking style.",
    )

    speaking_rate: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed multiplier.",
    )

    pitch: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Pitch multiplier.",
    )

    volume: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Relative output volume.",
    )

    pause_between_sentences: float = Field(
        default=0.25,
        ge=0.0,
        le=5.0,
        description="Pause duration between sentences (seconds).",
    )

    emotional_range: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Expressiveness of the voice.",
    )

    clarity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Speech clarity.",
    )

    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence level in delivery.",
    )

    pronunciation_hints: list[str] = Field(
        default_factory=list,
        description="Words or names requiring special pronunciation.",
    )

    catchphrases: list[str] = Field(
        default_factory=list,
        description="Frequently used phrases.",
    )

    notes: str | None = Field(
        default=None,
        description="Additional voice notes.",
    )

    @property
    def is_narrator(self) -> bool:
        """Return True if this is a narrator voice."""
        return self.tone == "narrator"

    @property
    def is_divine(self) -> bool:
        """Return True for divine or celestial voices."""
        return self.tone == "divine"

    @property
    def prompt(self) -> str:
        """
        Build a reusable prompt fragment for TTS providers.
        """
        parts = [
            f"{self.gender} voice",
            self.age.replace("_", " "),
            self.tone,
            self.speech_style,
            f"{self.accent} accent",
        ]

        if self.catchphrases:
            parts.append(
                "signature phrases: "
                + ", ".join(self.catchphrases)
            )

        return ", ".join(parts)