"""
src/models/components/camera.py

Camera settings used for cinematic shot generation.

This module defines reusable camera configuration shared across
Shots, Scenes, Storyboards and AI generation providers.

Author
------
Mahy Mythic Labs
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from src.models.base import ValueModel


CameraType = Literal[
    "cinema",
    "dslr",
    "drone",
    "handheld",
    "virtual",
    "action",
    "phone",
]

LensType = Literal[
    "14mm",
    "24mm",
    "35mm",
    "50mm",
    "85mm",
    "135mm",
    "200mm",
]

CameraMovement = Literal[
    "static",
    "pan_left",
    "pan_right",
    "tilt_up",
    "tilt_down",
    "dolly_in",
    "dolly_out",
    "truck_left",
    "truck_right",
    "crane_up",
    "crane_down",
    "orbit",
    "push_in",
    "pull_out",
    "zoom_in",
    "zoom_out",
]

CameraAngle = Literal[
    "eye_level",
    "high",
    "low",
    "bird_eye",
    "worm_eye",
    "overhead",
    "dutch",
]

ShotFraming = Literal[
    "extreme_wide",
    "wide",
    "full",
    "medium",
    "medium_close",
    "close_up",
    "extreme_close",
]

AspectRatio = Literal[
    "16:9",
    "9:16",
    "1:1",
    "4:3",
    "21:9",
]

FocusMode = Literal[
    "auto",
    "manual",
    "tracking",
    "face",
    "continuous",
]


class CameraSettings(ValueModel):
    """
    Reusable cinematic camera configuration.

    This object is shared across:

    - Shot
    - Scene
    - Storyboard
    - Video generation
    - Image generation
    """

    camera_type: CameraType = Field(
        default="cinema",
        description="Type of camera.",
    )

    lens: LensType = Field(
        default="35mm",
        description="Lens focal length.",
    )

    movement: CameraMovement = Field(
        default="static",
        description="Camera movement.",
    )

    angle: CameraAngle = Field(
        default="eye_level",
        description="Camera angle.",
    )

    framing: ShotFraming = Field(
        default="medium",
        description="Shot framing.",
    )

    focus_mode: FocusMode = Field(
        default="tracking",
        description="Focus mode.",
    )

    depth_of_field: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Relative depth of field.",
    )

    zoom: float = Field(
        default=1.0,
        ge=0.1,
        le=20.0,
        description="Zoom multiplier.",
    )

    fps: int = Field(
        default=24,
        ge=1,
        le=240,
        description="Frames per second.",
    )

    aspect_ratio: AspectRatio = Field(
        default="16:9",
        description="Output aspect ratio.",
    )

    stabilization: bool = Field(
        default=True,
        description="Enable camera stabilization.",
    )

    motion_blur: bool = Field(
        default=True,
        description="Enable motion blur.",
    )

    cinematic: bool = Field(
        default=True,
        description="Apply cinematic camera style.",
    )

    def is_dynamic(self) -> bool:
        """
        Returns True if the camera is moving.
        """
        return self.movement != "static"

    def is_zoomed(self) -> bool:
        """
        Returns True if zoom is applied.
        """
        return self.zoom != 1.0

    @property
    def prompt(self) -> str:
        """
        Build a reusable prompt fragment for AI generation.

        Example
        -------
        cinema camera, 35mm lens, dolly_in,
        eye_level angle, medium framing
        """
        return (
            f"{self.camera_type} camera, "
            f"{self.lens} lens, "
            f"{self.movement}, "
            f"{self.angle} angle, "
            f"{self.framing} framing"
        )