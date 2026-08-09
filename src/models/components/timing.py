"""
src/models/components/timing.py

Reusable timing configuration for Mahy Mythic Labs Studio OS.

This module defines timing and pacing information shared across
shots, scenes, storyboards, rendering, narration and subtitle
generation.

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


TimingMode = Literal[
    "automatic",
    "manual",
]

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
]


class TimingSettings(ValueModel):
    """
    Reusable timing configuration.

    Used by

    - Shot
    - Scene
    - Storyboard
    - Timeline
    - Video Rendering
    """

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    start_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Start time (seconds).",
    )

    end_time: float = Field(
        default=5.0,
        ge=0.0,
        description="End time (seconds).",
    )

    duration: float = Field(
        default=5.0,
        gt=0.0,
        description="Shot duration (seconds).",
    )

    mode: TimingMode = Field(
        default="automatic",
        description="Timeline mode.",
    )

    # ------------------------------------------------------------------
    # Transition
    # ------------------------------------------------------------------

    transition_in: TransitionType = Field(
        default="cut",
        description="Incoming transition.",
    )

    transition_out: TransitionType = Field(
        default="cut",
        description="Outgoing transition.",
    )

    transition_duration: float = Field(
        default=0.5,
        ge=0.0,
        le=10.0,
        description="Transition duration (seconds).",
    )

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    narration_offset: float = Field(
        default=0.0,
        description="Narration offset in seconds.",
    )

    subtitle_offset: float = Field(
        default=0.0,
        description="Subtitle offset in seconds.",
    )

    music_offset: float = Field(
        default=0.0,
        description="Background music offset.",
    )

    sound_effect_offset: float = Field(
        default=0.0,
        description="Sound effect offset.",
    )

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    playback_speed: float = Field(
        default=1.0,
        gt=0.1,
        le=4.0,
        description="Playback speed multiplier.",
    )

    loop: bool = Field(
        default=False,
        description="Loop playback.",
    )

    freeze_last_frame: bool = Field(
        default=False,
        description="Freeze the last frame.",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def actual_duration(self) -> float:
        """
        Calculate effective duration after playback speed.
        """
        return self.duration / self.playback_speed

    @property
    def timeline_range(self) -> tuple[float, float]:
        """
        Return (start, end) timeline.
        """
        return (self.start_time, self.end_time)

    @property
    def has_transition(self) -> bool:
        """
        Whether the shot has transitions.
        """
        return (
            self.transition_in != "cut"
            or self.transition_out != "cut"
        )

    @property
    def has_audio_offsets(self) -> bool:
        """
        Whether any audio track is offset.
        """
        return any(
            value != 0.0
            for value in (
                self.narration_offset,
                self.music_offset,
                self.sound_effect_offset,
            )
        )

    def is_slow_motion(self) -> bool:
        """
        Returns True when playback speed is below real-time.
        """
        return self.playback_speed < 1.0

    def is_fast_motion(self) -> bool:
        """
        Returns True when playback speed is above real-time.
        """
        return self.playback_speed > 1.0

    @property
    def prompt(self) -> str:
        """
        Human-readable timing summary.
        """
        return (
            f"{self.duration:.1f}s, "
            f"{self.transition_in} → {self.transition_out}, "
            f"{self.playback_speed:.1f}x"
        )