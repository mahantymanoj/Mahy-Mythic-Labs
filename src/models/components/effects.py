"""
src/models/components/effects.py

Reusable visual effects configuration for Mahy Mythic Labs Studio OS.

This module defines cinematic visual effects shared across
shots, scenes, storyboards and AI generation providers.

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


ParticleEffect = Literal[
    "none",
    "dust",
    "ash",
    "embers",
    "sparks",
    "snow",
    "rain",
    "petals",
    "leaves",
    "magic_particles",
]

AtmosphericEffect = Literal[
    "none",
    "fog",
    "mist",
    "smoke",
    "haze",
    "clouds",
    "volumetric_light",
]

WeatherEffect = Literal[
    "none",
    "rain",
    "storm",
    "lightning",
    "snow",
    "sandstorm",
]

MagicEffect = Literal[
    "none",
    "divine_aura",
    "holy_light",
    "energy_field",
    "cosmic_energy",
    "celestial_glow",
    "chakra",
]

PostProcessing = Literal[
    "none",
    "bloom",
    "lens_flare",
    "film_grain",
    "chromatic_aberration",
    "motion_blur",
    "depth_of_field",
]


class EffectsSettings(ValueModel):
    """
    Reusable cinematic effects configuration.

    Shared by

    - Shot
    - Scene
    - Storyboard
    - Image Generation
    - Video Generation
    """

    particle_effect: ParticleEffect = Field(
        default="none",
        description="Primary particle effect.",
    )

    atmospheric_effect: AtmosphericEffect = Field(
        default="none",
        description="Atmospheric effect.",
    )

    weather_effect: WeatherEffect = Field(
        default="none",
        description="Weather-based visual effect.",
    )

    magic_effect: MagicEffect = Field(
        default="none",
        description="Mythological or energy effect.",
    )

    post_processing: list[PostProcessing] = Field(
        default_factory=list,
        description="Post-processing effects.",
    )

    effect_intensity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Overall effect intensity.",
    )

    glow_strength: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Glow intensity.",
    )

    particle_density: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Particle density.",
    )

    enable_reflections: bool = Field(
        default=True,
        description="Enable reflective surfaces.",
    )

    enable_refractions: bool = Field(
        default=False,
        description="Enable refraction effects.",
    )

    enable_shadows: bool = Field(
        default=True,
        description="Enable dynamic shadows.",
    )

    enable_ray_tracing: bool = Field(
        default=False,
        description="Prefer ray-traced rendering where supported.",
    )

    custom_effects: list[str] = Field(
        default_factory=list,
        description="Additional provider-specific effect hints.",
    )

    @property
    def has_particles(self) -> bool:
        """Return True if particle effects are enabled."""
        return self.particle_effect != "none"

    @property
    def has_magic(self) -> bool:
        """Return True if a magical effect is enabled."""
        return self.magic_effect != "none"

    @property
    def has_weather(self) -> bool:
        """Return True if a weather effect is enabled."""
        return self.weather_effect != "none"

    @property
    def has_post_processing(self) -> bool:
        """Return True if post-processing effects are configured."""
        return len(self.post_processing) > 0

    @property
    def prompt(self) -> str:
        """
        Build a reusable prompt fragment.
        """
        parts: list[str] = []

        if self.particle_effect != "none":
            parts.append(self.particle_effect.replace("_", " "))

        if self.atmospheric_effect != "none":
            parts.append(self.atmospheric_effect.replace("_", " "))

        if self.weather_effect != "none":
            parts.append(self.weather_effect.replace("_", " "))

        if self.magic_effect != "none":
            parts.append(self.magic_effect.replace("_", " "))

        parts.extend(
            effect.replace("_", " ")
            for effect in self.post_processing
            if effect != "none"
        )

        parts.extend(self.custom_effects)

        return ", ".join(parts)