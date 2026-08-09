"""Pipeline Context for Mahy Mythic Labs Data Engineering Engine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from src.models.episode import EpisodeConfig, EpisodeState


@dataclass
class PipelineContext:
    """Shared pipeline execution context containing episode configuration and paths."""

    config: EpisodeConfig
    state: EpisodeState
    projects_root: Path = Path("projects")
    data: Dict[str, Any] = field(default_factory=dict)

    @property
    def episode_dir(self) -> Path:
        return self.projects_root / self.config.episode_id

    @property
    def state_file(self) -> Path:
        return self.episode_dir / "state.json"

    def get_path(self, relative_subpath: str) -> Path:
        p = self.episode_dir / relative_subpath
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
