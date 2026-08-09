"""
src/models/components/render.py

Reusable rendering configuration for Mahy Mythic Labs Studio OS.

Defines output rendering preferences shared across image generation,
video generation and post-processing pipelines.

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


Resolution = Literal[
    "480p",
    "720p",
    "1080p",
    "1440p",
    "2160p",
    "4k",
    "8k",
]

AspectRatio = Literal[
    "1:1",
    "4:3",
    "16:9",
    "9:16",
    "21:9",
]

VideoCodec = Literal[
    "h264",
    "h265",
    "av1",
    "prores",
]

ImageFormat = Literal[
    "png",
    "jpeg",
    "webp",
]

VideoFormat = Literal[
    "mp4",
    "mov",
    "mkv",
]

FrameInterpolation = Literal[
    "none",
    "optical_flow",
    "ai",
]


class RenderSettings(ValueModel):
    """
    Rendering configuration.

    Shared by

    - Shot
    - Scene
    - Storyboard
    - Rendering Pipeline
    """

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    resolution: Resolution = Field(
        default="1080p",
    )

    aspect_ratio: AspectRatio = Field(
        default="16:9",
    )

    fps: int = Field(
        default=30,
        ge=1,
        le=240,
    )

    duration_seconds: float = Field(
        default=5.0,
        gt=0.0,
    )

    # ------------------------------------------------------------------
    # Formats
    # ------------------------------------------------------------------

    image_format: ImageFormat = Field(
        default="png",
    )

    video_format: VideoFormat = Field(
        default="mp4",
    )

    video_codec: VideoCodec = Field(
        default="h264",
    )

    # ------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------

    bitrate_mbps: int = Field(
        default=20,
        ge=1,
        le=500,
    )

    quality: int = Field(
        default=95,
        ge=1,
        le=100,
    )

    frame_interpolation: FrameInterpolation = Field(
        default="none",
    )

    anti_aliasing: bool = Field(
        default=True,
    )

    hdr: bool = Field(
        default=True,
    )

    alpha_channel: bool = Field(
        default=False,
    )

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    export_audio: bool = Field(
        default=True,
    )

    export_subtitles: bool = Field(
        default=False,
    )

    embed_metadata: bool = Field(
        default=True,
    )

    overwrite_existing: bool = Field(
        default=False,
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def is_vertical(self) -> bool:
        """True for portrait-oriented outputs."""
        return self.aspect_ratio == "9:16"

    @property
    def is_horizontal(self) -> bool:
        """True for landscape-oriented outputs."""
        return self.aspect_ratio in {
            "16:9",
            "21:9",
        }

    @property
    def is_ultra_hd(self) -> bool:
        """True for UHD rendering."""
        return self.resolution in {
            "2160p",
            "4k",
            "8k",
        }

    @property
    def uses_ai_interpolation(self) -> bool:
        """True when AI frame interpolation is enabled."""
        return self.frame_interpolation == "ai"

    @property
    def output_extension(self) -> str:
        """Return the video file extension."""
        return self.video_format

    @property
    def prompt(self) -> str:
        """
        Human-readable render summary.
        """
        return (
            f"{self.resolution}, "
            f"{self.aspect_ratio}, "
            f"{self.fps}fps, "
            f"{self.video_codec}"
        )
    