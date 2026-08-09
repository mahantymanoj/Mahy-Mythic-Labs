"""
src/models/components/lighting.py

Reusable cinematic lighting configuration for Studio OS.

This module defines lighting settings shared across shots,
scenes, storyboards, and AI generation providers.

Author
------
Mahy Mythic Labs
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from src.models.base import ValueModel


LightingStyle = Literal[
    "natural",
    "cinematic",
    "dramatic",
    "rembrandt",
    "film_noir",
    "high_key",
    "low_key",
    "studio",
    "volumetric",
    "golden_hour",
    "blue_hour",
    "moonlight",
    "torchlight",
    "candlelight",
]

LightDirection = Literal[
    "front",
    "back",
    "side_left",
    "side_right",
    "top",
    "bottom",
    "rim",
    "ambient",
]

TimeOfDay = Literal[
    "sunrise",
    "morning",
    "noon",
    "afternoon",
    "sunset",
    "evening",
    "night",
]

WeatherCondition = Literal[
    "clear",
    "cloudy",
    "fog",
    "mist",
    "rain",
    "storm",
    "snow",
]

ColorTemperature = Literal[
    "warm",
    "neutral",
    "cool",
]


class LightingSettings(ValueModel):
    """
    Reusable cinematic lighting configuration.

    Used by

    - Shot
    - Scene
    - Storyboard
    - Image Generation
    - Video Generation
    """

    style: LightingStyle = Field(
        default="cinematic",
        description="Primary lighting style.",
    )

    direction: LightDirection = Field(
        default="front",
        description="Dominant light direction.",
    )

    intensity: float = Field(
        default=0.8,
        ge=0.0,
        le=2.0,
        description="Relative light intensity.",
    )

    color_temperature: ColorTemperature = Field(
        default="neutral",
        description="Lighting color temperature.",
    )

    time_of_day: TimeOfDay = Field(
        default="afternoon",
        description="Time of day.",
    )

    weather: WeatherCondition = Field(
        default="clear",
        description="Weather affecting lighting.",
    )

    shadows: bool = Field(
        default=True,
        description="Enable shadows.",
    )

    soft_shadows: bool = Field(
        default=True,
        description="Use soft shadows.",
    )

    volumetric_light: bool = Field(
        default=False,
        description="Enable volumetric lighting.",
    )

    reflections: bool = Field(
        default=True,
        description="Enable realistic reflections.",
    )

    bloom: bool = Field(
        default=False,
        description="Enable bloom effect.",
    )

    global_illumination: bool = Field(
        default=True,
        description="Use global illumination.",
    )

    hdr: bool = Field(
        default=True,
        description="Enable HDR lighting.",
    )

    def is_night_scene(self) -> bool:
        """
        Returns True if the scene takes place at night.
        """
        return self.time_of_day in {"night", "moonlight"}

    def has_volumetric_effects(self) -> bool:
        """
        Returns True when volumetric lighting is enabled.
        """
        return self.volumetric_light

    @property
    def prompt(self) -> str:
        """
        Build a reusable prompt fragment.

        Example
        -------
        cinematic lighting,
        warm color temperature,
        golden hour,
        front lighting,
        volumetric light
        """
        parts = [
            f"{self.style} lighting",
            f"{self.color_temperature} color temperature",
            self.time_of_day.replace("_", " "),
            f"{self.direction} lighting",
        ]

        if self.volumetric_light:
            parts.append("volumetric lighting")

        if self.soft_shadows:
            parts.append("soft shadows")

        if self.hdr:
            parts.append("HDR")

        return ", ".join(parts)