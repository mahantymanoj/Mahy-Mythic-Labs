"""Storyboard data models for Mahy Mythic Labs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VisualPrompt:
    positive_prompt: str
    negative_prompt: str = "text, watermark, low quality, blurry, disfigured"
    aspect_ratio: str = "9:16"
    style: str = "cinematic"


@dataclass
class AudioCue:
    narration_audio_path: Optional[str] = None
    music_track: Optional[str] = None
    sfx_cue: Optional[str] = None


@dataclass
class Shot:
    shot_id: str
    scene_number: int
    shot_number: int
    duration_seconds: float
    visual_prompt: VisualPrompt
    audio_cue: AudioCue
    generated_image_path: Optional[str] = None
    generated_video_path: Optional[str] = None


@dataclass
class Storyboard:
    episode_id: str
    shots: List[Shot] = field(default_factory=list)
    total_shots: int = 0
