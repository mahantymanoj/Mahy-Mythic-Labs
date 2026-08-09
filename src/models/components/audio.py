"""
src/models/components/audio.py

Reusable audio configuration for Mahy Mythic Labs Studio OS.

This module defines audio settings shared across shots,
scenes, storyboards and rendering.

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


NarrationStyle = Literal[
    "documentary",
    "cinematic",
    "storytelling",
    "conversational",
    "dramatic",
]

VoiceGender = Literal[
    "male",
    "female",
    "neutral",
]

MusicGenre = Literal[
    "cinematic",
    "orchestral",
    "epic",
    "ambient",
    "traditional",
    "electronic",
    "none",
]

AudioFormat = Literal[
    "mp3",
    "wav",
    "flac",
    "aac",
]

Emotion = Literal[
    "neutral",
    "happy",
    "sad",
    "angry",
    "fear",
    "mysterious",
    "epic",
    "divine",
]


class AudioSettings(ValueModel):
    """
    Reusable audio configuration.

    Shared by

    - Shot
    - Scene
    - Storyboard
    - Rendering
    """

    # ------------------------------------------------------------------
    # Narration
    # ------------------------------------------------------------------

    narration_text: str = Field(
        default="",
        description="Narration script.",
    )

    narration_style: NarrationStyle = Field(
        default="documentary",
    )

    voice_name: str = Field(
        default="",
        description="Preferred voice identifier.",
    )

    voice_gender: VoiceGender = Field(
        default="male",
    )

    emotion: Emotion = Field(
        default="neutral",
    )

    speech_rate: float = Field(
        default=1.0,
        gt=0.5,
        le=2.0,
        description="Speech speed multiplier.",
    )

    pitch: float = Field(
        default=1.0,
        gt=0.5,
        le=2.0,
        description="Voice pitch multiplier.",
    )

    # ------------------------------------------------------------------
    # Background Music
    # ------------------------------------------------------------------

    music_enabled: bool = Field(
        default=True,
    )

    music_genre: MusicGenre = Field(
        default="cinematic",
    )

    music_description: str = Field(
        default="Epic orchestral cinematic background music.",
    )

    music_volume: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
    )

    # ------------------------------------------------------------------
    # Ambient Audio
    # ------------------------------------------------------------------

    ambience_enabled: bool = Field(
        default=True,
    )

    ambience_description: str = Field(
        default="Natural environmental ambience.",
    )

    ambience_volume: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
    )

    # ------------------------------------------------------------------
    # Sound Effects
    # ------------------------------------------------------------------

    sfx_enabled: bool = Field(
        default=True,
    )

    sound_effects: list[str] = Field(
        default_factory=list,
        description="Sound effect descriptions.",
    )

    sfx_volume: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
    )

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    audio_format: AudioFormat = Field(
        default="wav",
    )

    sample_rate: int = Field(
        default=48000,
        ge=8000,
        le=192000,
    )

    normalize_audio: bool = Field(
        default=True,
    )

    noise_reduction: bool = Field(
        default=True,
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def has_narration(self) -> bool:
        """Return True when narration text exists."""
        return bool(self.narration_text.strip())

    @property
    def has_music(self) -> bool:
        """Return True when background music is enabled."""
        return (
            self.music_enabled
            and self.music_genre != "none"
        )

    @property
    def has_ambience(self) -> bool:
        """Return True when ambience is enabled."""
        return self.ambience_enabled

    @property
    def has_sound_effects(self) -> bool:
        """Return True when sound effects exist."""
        return (
            self.sfx_enabled
            and len(self.sound_effects) > 0
        )

    @property
    def total_mix_level(self) -> float:
        """
        Combined audio mix level.

        Useful for validation.
        """
        return (
            self.music_volume
            + self.ambience_volume
            + self.sfx_volume
        )

    @property
    def prompt(self) -> str:
        """
        Human-readable audio summary.
        """
        parts = []

        if self.has_narration:
            parts.append(
                f"{self.narration_style} narration"
            )

        if self.has_music:
            parts.append(
                f"{self.music_genre} music"
            )

        if self.has_ambience:
            parts.append(
                "environment ambience"
            )

        if self.has_sound_effects:
            parts.append(
                "cinematic sound effects"
            )

        return ", ".join(parts)