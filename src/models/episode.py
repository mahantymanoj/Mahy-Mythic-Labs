"""Episode data models for Mahy Mythic Labs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.enums import EpisodeFormat, WorkflowStatus


@dataclass
class EpisodeConfig:
    episode_id: str
    title: str
    domain: str = "astronomy"
    format: EpisodeFormat = EpisodeFormat.SHORT_9_16
    target_duration_seconds: int = 60
    language: str = "en"
    voice_name: str = "en-US-ChristopherNeural"
    style_prompt: str = "cinematic documentary style, dramatic lighting, high detail"


@dataclass
class EpisodeState:
    episode_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_stage: str = "init"
    completed_stages: List[str] = field(default_factory=list)
    stage_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class Episode:
    config: EpisodeConfig
    state: EpisodeState
    project_dir: str
