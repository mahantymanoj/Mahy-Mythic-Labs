"""StateManager for idempotent task checkpoints in projects/EPxxx/state.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from src.enums import WorkflowStatus
from src.models.episode import EpisodeState


class StateManager:
    """Persist and load pipeline state checkpoints for episode production runs."""

    @staticmethod
    def load(state_path: Path, episode_id: str) -> EpisodeState:
        """Load state checkpoint if present, or return new EpisodeState."""
        if not state_path.exists():
            return EpisodeState(episode_id=episode_id)

        try:
            with open(state_path, "r", encoding="utf-8") as file:
                raw = json.load(file)
            return EpisodeState(
                episode_id=raw.get("episode_id", episode_id),
                status=WorkflowStatus(raw.get("status", "pending")),
                current_stage=raw.get("current_stage", "init"),
                completed_stages=raw.get("completed_stages", []),
                stage_data=raw.get("stage_data", {}),
                errors=raw.get("errors", []),
            )
        except Exception:
            return EpisodeState(episode_id=episode_id)

    @staticmethod
    def save(state_path: Path, state: EpisodeState) -> None:
        """Write current EpisodeState checkpoint to disk."""
        state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "episode_id": state.episode_id,
            "status": state.status.value,
            "current_stage": state.current_stage,
            "completed_stages": state.completed_stages,
            "stage_data": state.stage_data,
            "errors": state.errors,
        }
        with open(state_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
