"""Asset data models for Mahy Mythic Labs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from src.enums import AssetType, GenerationStatus, ProviderBackend


@dataclass
class MediaAsset:
    asset_id: str
    asset_type: AssetType
    file_path: str
    status: GenerationStatus = GenerationStatus.COMPLETED
    provider: ProviderBackend = ProviderBackend.FREE_EDGE_TTS
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
