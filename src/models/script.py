"""Script data models for Mahy Mythic Labs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class NarrationBlock:
    id: str
    text: str
    duration_estimate_seconds: float = 0.0
    audio_path: Optional[str] = None


@dataclass
class Scene:
    scene_number: int
    title: str
    narration: NarrationBlock
    visual_description: str
    duration_seconds: float = 5.0
    keywords: List[str] = field(default_factory=list)


@dataclass
class Section:
    section_number: int
    title: str
    scenes: List[Scene] = field(default_factory=list)


@dataclass
class Script:
    title: str
    hook: str
    sections: List[Section] = field(default_factory=list)
    call_to_action: str = ""
    total_estimated_duration: float = 0.0
