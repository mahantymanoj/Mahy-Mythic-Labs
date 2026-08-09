"""
src/models/components/transition.py

Reusable cinematic transition configuration for Mahy Mythic Labs Studio OS.

This module defines transitions used between shots and scenes.

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


TransitionType = Literal[
    "cut",
    "fade",
    "fade_to_black",
    "fade_to_white",
    "cross_dissolve",
    "wipe",
    "zoom",
    "whip_pan",
    "match_cut",
    "iris",
    "blur",
    "slide",
]

TransitionDirection = Literal[
    "left",
    "right",
    "up",
    "down",
    "center",
    "none",
]

TransitionCurve = Literal[
    "linear",
    "ease_in",
    "ease_out",
    "ease_in_out",
]


class TransitionSettings(ValueModel):
    """
    Reusable cinematic transition configuration.

    Used by

    - Shot
    - Scene
    - Storyboard
    - Timeline
    - Video Rendering
    """

    transition_type: TransitionType = Field(
        default="cut",
        description="Transition effect.",
    )

    duration: float = Field(
        default=0.5,
        ge=0.0,
        le=10.0,
        description="Transition duration (seconds).",
    )

    direction: TransitionDirection = Field(
        default="none",
        description="Transition direction.",
    )

    curve: TransitionCurve = Field(
        default="ease_in_out",
        description="Transition animation curve.",
    )

    speed: float = Field(
        default=1.0,
        gt=0.1,
        le=5.0,
        description="Transition speed multiplier.",
    )

    overlap_audio: bool = Field(
        default=True,
        description="Crossfade audio during transition.",
    )

    preserve_music: bool = Field(
        default=True,
        description="Keep background music continuous.",
    )

    preserve_ambience: bool = Field(
        default=True,
        description="Keep ambient sound continuous.",
    )

    apply_motion_blur: bool = Field(
        default=False,
        description="Apply motion blur during transition.",
    )

    cinematic: bool = Field(
        default=True,
        description="Use cinematic transition behaviour.",
    )

    @property
    def is_cut(self) -> bool:
        """Return True if transition is an instant cut."""
        return self.transition_type == "cut"

    @property
    def is_animated(self) -> bool:
        """Return True if the transition has animation."""
        return self.transition_type != "cut"

    @property
    def effective_duration(self) -> float:
        """
        Transition duration after speed adjustment.
        """
        return self.duration / self.speed

    @property
    def prompt(self) -> str:
        """
        Human-readable transition summary.
        """
        if self.direction == "none":
            return (
                f"{self.transition_type}, "
                f"{self.duration:.1f}s"
            )

        return (
            f"{self.transition_type}, "
            f"{self.direction}, "
            f"{self.duration:.1f}s"
        )