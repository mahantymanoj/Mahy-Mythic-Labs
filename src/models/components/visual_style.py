"""
src/models/components/visual_style.py

Reusable visual style configuration for Mahy Mythic Labs Studio OS.

This module defines the artistic identity shared across shots,
scenes, storyboards and AI generation providers.

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


RenderStyle = Literal[
    "photorealistic",
    "hyperrealistic",
    "cinematic",
    "documentary",
    "stylized",
]

ColorGrade = Literal[
    "natural",
    "warm",
    "cool",
    "teal_orange",
    "golden",
    "desaturated",
    "high_contrast",
    "monochrome",
]

MoodStyle = Literal[
    "epic",
    "mystical",
    "divine",
    "dark",
    "peaceful",
    "dramatic",
    "hopeful",
    "ancient",
]

FilmLook = Literal[
    "digital",
    "35mm",
    "70mm",
    "imax",
]

ImageQuality = Literal[
    "draft",
    "standard",
    "high",
    "ultra",
]


class VisualStyleSettings(ValueModel):
    """
    Reusable visual identity.

    Shared by

    - Project
    - Episode
    - Scene
    - Shot
    - Image Generation
    - Video Generation
    """

    render_style: RenderStyle = Field(
        default="cinematic",
        description="Primary rendering style.",
    )

    image_quality: ImageQuality = Field(
        default="high",
        description="Desired output quality.",
    )

    mood: MoodStyle = Field(
        default="epic",
        description="Overall emotional tone.",
    )

    color_grade: ColorGrade = Field(
        default="teal_orange",
        description="Color grading preset.",
    )

    film_look: FilmLook = Field(
        default="35mm",
        description="Film stock aesthetic.",
    )

    saturation: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Color saturation multiplier.",
    )

    contrast: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Contrast multiplier.",
    )

    brightness: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Brightness multiplier.",
    )

    sharpness: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Sharpness multiplier.",
    )

    realism: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Target realism level.",
    )

    cinematic: bool = Field(
        default=True,
        description="Favor cinematic visuals.",
    )

    hdr: bool = Field(
        default=True,
        description="Enable HDR look.",
    )

    depth_enhancement: bool = Field(
        default=True,
        description="Enhance scene depth.",
    )

    volumetric_effects: bool = Field(
        default=True,
        description="Enable volumetric lighting effects.",
    )

    lens_flare: bool = Field(
        default=False,
        description="Allow subtle cinematic lens flares.",
    )

    film_grain: bool = Field(
        default=False,
        description="Apply film grain.",
    )

    vignette: bool = Field(
        default=False,
        description="Apply vignette effect.",
    )

    style_tags: list[str] = Field(
        default_factory=list,
        description="Additional artistic style tags.",
    )

    @property
    def is_photorealistic(self) -> bool:
        """Return True when realism is the target."""
        return self.render_style in {
            "photorealistic",
            "hyperrealistic",
        }

    @property
    def is_cinematic(self) -> bool:
        """Return True when cinematic rendering is enabled."""
        return self.cinematic

    @property
    def prompt(self) -> str:
        """
        Build a reusable prompt fragment.
        """
        parts = [
            self.render_style,
            self.color_grade.replace("_", " "),
            self.mood,
            self.film_look,
        ]

        if self.hdr:
            parts.append("HDR")

        if self.depth_enhancement:
            parts.append("depth enhanced")

        if self.volumetric_effects:
            parts.append("volumetric lighting")

        if self.lens_flare:
            parts.append("subtle lens flare")

        if self.film_grain:
            parts.append("film grain")

        if self.vignette:
            parts.append("vignette")

        parts.extend(self.style_tags)

        return ", ".join(parts)