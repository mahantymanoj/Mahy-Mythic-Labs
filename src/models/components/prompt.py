"""
src/models/components/prompt.py

Reusable prompt models for Mahy Mythic Labs Studio OS.

This module defines the prompt structures used throughout the
AI production pipeline. A PromptSet represents the complete
creative intent for a shot, scene, or asset and can be adapted
to multiple AI providers.

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


PromptQuality = Literal[
    "draft",
    "standard",
    "high",
    "ultra",
]

PromptLanguage = Literal[
    "english",
    "hindi",
    "odia",
    "gujarati",
]


class PromptSet(ValueModel):
    """
    Complete reusable prompt definition.

    A PromptSet is provider-independent.

    The Master Director can transform these prompts into
    provider-specific prompts for GPT, Gemini, Flux,
    Runway, Veo, Kling, etc.
    """

    # ------------------------------------------------------------------
    # Master Prompt
    # ------------------------------------------------------------------

    master_prompt: str = Field(
        default="",
        description="Primary cinematic prompt.",
    )

    # ------------------------------------------------------------------
    # Provider Prompts
    # ------------------------------------------------------------------

    image_prompt: str = Field(
        default="",
        description="Prompt used for image generation.",
    )

    video_prompt: str = Field(
        default="",
        description="Prompt used for video generation.",
    )

    narration_prompt: str = Field(
        default="",
        description="Prompt for narration generation.",
    )

    music_prompt: str = Field(
        default="",
        description="Prompt for music generation.",
    )

    sound_effect_prompt: str = Field(
        default="",
        description="Prompt for ambient sound generation.",
    )

    # ------------------------------------------------------------------
    # Negative Prompt
    # ------------------------------------------------------------------

    negative_prompt: str = Field(
        default="",
        description="Negative prompt shared across providers.",
    )

    # ------------------------------------------------------------------
    # Creative Direction
    # ------------------------------------------------------------------

    artistic_style: str = Field(
        default="cinematic realism",
        description="Overall artistic direction.",
    )

    mood: str = Field(
        default="epic",
        description="Creative mood.",
    )

    visual_style: str = Field(
        default="photorealistic",
        description="Visual rendering style.",
    )

    color_palette: str = Field(
        default="natural",
        description="Preferred color palette.",
    )

    # ------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------

    quality: PromptQuality = Field(
        default="high",
        description="Prompt quality preset.",
    )

    language: PromptLanguage = Field(
        default="english",
        description="Prompt language.",
    )

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    references: list[str] = Field(
        default_factory=list,
        description="Reference URLs or identifiers.",
    )

    keywords: list[str] = Field(
        default_factory=list,
        description="Important keywords.",
    )

    banned_words: list[str] = Field(
        default_factory=list,
        description="Words to avoid.",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def has_negative_prompt(self) -> bool:
        """Return True when a negative prompt is defined."""
        return bool(self.negative_prompt.strip())

    @property
    def has_image_prompt(self) -> bool:
        """Return True when an image prompt exists."""
        return bool(self.image_prompt.strip())

    @property
    def has_video_prompt(self) -> bool:
        """Return True when a video prompt exists."""
        return bool(self.video_prompt.strip())

    @property
    def has_music_prompt(self) -> bool:
        """Return True when a music prompt exists."""
        return bool(self.music_prompt.strip())

    def add_keyword(self, keyword: str) -> "PromptSet":
        """
        Return a new PromptSet with an additional keyword.
        """
        if keyword in self.keywords:
            return self

        return self.replace(
            keywords=[*self.keywords, keyword]
        )

    def remove_keyword(self, keyword: str) -> "PromptSet":
        """
        Return a new PromptSet with a keyword removed.
        """
        return self.replace(
            keywords=[
                value
                for value in self.keywords
                if value != keyword
            ]
        )

    @property
    def summary(self) -> str:
        """
        Short human-readable summary.
        """
        return (
            f"{self.artistic_style}, "
            f"{self.visual_style}, "
            f"{self.mood}"
        )

    @property
    def prompt(self) -> str:
        """
        Canonical prompt used by the Master Director.
        """
        if self.master_prompt:
            return self.master_prompt

        return self.image_prompt or self.video_prompt