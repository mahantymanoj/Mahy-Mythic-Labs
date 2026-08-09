"""
src/models/components/composition.py

Reusable composition configuration for Mahy Mythic Labs Studio OS.

This module defines visual composition principles shared across
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


CompositionStyle = Literal[
    "balanced",
    "dynamic",
    "symmetrical",
    "asymmetrical",
    "minimal",
    "epic",
]

FramingRule = Literal[
    "rule_of_thirds",
    "golden_ratio",
    "centered",
    "symmetry",
    "leading_lines",
    "none",
]

DepthStyle = Literal[
    "flat",
    "shallow",
    "moderate",
    "deep",
]

SubjectPosition = Literal[
    "left",
    "center",
    "right",
]

EyeLine = Literal[
    "camera",
    "left",
    "right",
    "up",
    "down",
]

ForegroundEmphasis = Literal[
    "none",
    "low",
    "medium",
    "high",
]


class CompositionSettings(ValueModel):
    """
    Reusable composition settings.

    Shared by

    - Shot
    - Scene
    - Storyboard
    - Image Generation
    - Video Generation
    """

    style: CompositionStyle = Field(
        default="balanced",
        description="Overall composition style.",
    )

    framing_rule: FramingRule = Field(
        default="rule_of_thirds",
        description="Primary framing principle.",
    )

    subject_position: SubjectPosition = Field(
        default="center",
        description="Primary subject placement.",
    )

    eye_line: EyeLine = Field(
        default="camera",
        description="Subject eye-line direction.",
    )

    depth: DepthStyle = Field(
        default="moderate",
        description="Scene depth.",
    )

    foreground_emphasis: ForegroundEmphasis = Field(
        default="medium",
        description="Foreground prominence.",
    )

    background_emphasis: ForegroundEmphasis = Field(
        default="medium",
        description="Background prominence.",
    )

    negative_space: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Relative amount of negative space.",
    )

    horizon_level: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Vertical horizon position.",
    )

    subject_scale: float = Field(
        default=0.50,
        ge=0.05,
        le=1.00,
        description="Relative subject size in frame.",
    )

    leading_lines: bool = Field(
        default=True,
        description="Use leading lines.",
    )

    frame_with_objects: bool = Field(
        default=False,
        description="Use natural framing elements.",
    )

    symmetry: bool = Field(
        default=False,
        description="Prefer symmetrical composition.",
    )

    reflections: bool = Field(
        default=False,
        description="Use reflective surfaces.",
    )

    silhouette: bool = Field(
        default=False,
        description="Render as a silhouette when appropriate.",
    )

    cinematic_balance: bool = Field(
        default=True,
        description="Favor cinematic composition.",
    )

    @property
    def uses_rule_of_thirds(self) -> bool:
        """Return True when using the rule of thirds."""
        return self.framing_rule == "rule_of_thirds"

    @property
    def is_centered(self) -> bool:
        """Return True when the subject is centered."""
        return self.subject_position == "center"

    @property
    def has_strong_depth(self) -> bool:
        """Return True for compositions with pronounced depth."""
        return self.depth in {"moderate", "deep"}

    @property
    def prompt(self) -> str:
        """
        Build a reusable prompt fragment.
        """
        parts = [
            self.style,
            self.framing_rule.replace("_", " "),
            f"{self.subject_position} subject",
            f"{self.depth} depth",
        ]

        if self.leading_lines:
            parts.append("leading lines")

        if self.frame_with_objects:
            parts.append("natural framing")

        if self.symmetry:
            parts.append("symmetrical composition")

        if self.reflections:
            parts.append("reflections")

        if self.silhouette:
            parts.append("silhouette")

        return ", ".join(parts)