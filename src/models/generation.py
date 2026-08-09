"""
src/models/generation.py

AI Generation domain models.

Represents a single AI generation request and its result.

This module contains ONLY domain models.
Provider implementations belong to src/providers/.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import StudioBaseModel


# ==============================================================================
# Enums
# ==============================================================================


class GenerationType(str, Enum):
    """Supported generation types."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    THUMBNAIL = "thumbnail"
    EMBEDDING = "embedding"


class GenerationStatus(str, Enum):
    """Lifecycle of a generation request."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FinishReason(str, Enum):
    """Why generation finished."""

    SUCCESS = "success"
    LENGTH = "length"
    STOP = "stop"
    ERROR = "error"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


# ==============================================================================
# Prompt Models
# ==============================================================================


class Prompt(StudioBaseModel):
    """
    Prompt used for generation.
    """

    positive: str = Field(..., min_length=1)

    negative: Optional[str] = None

    system: Optional[str] = None

    template: Optional[str] = None

    variables: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# Generation Parameters
# ==============================================================================


class GenerationParameters(StudioBaseModel):
    """
    Generic generation parameters.
    """

    model_name: Optional[str] = None

    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)

    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    seed: Optional[int] = None

    width: Optional[int] = Field(default=None, ge=1)

    height: Optional[int] = Field(default=None, ge=1)

    duration_seconds: Optional[int] = Field(default=None, ge=1)

    fps: Optional[int] = Field(default=None, ge=1)

    quality: Optional[str] = None

    extra: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# Generation Result
# ==============================================================================


class GenerationResult(StudioBaseModel):
    """
    Output produced by an AI provider.
    """

    output_text: Optional[str] = None

    output_uri: Optional[str] = None

    preview_uri: Optional[str] = None

    checksum: Optional[str] = None

    mime_type: Optional[str] = None

    file_size_bytes: Optional[int] = Field(default=None, ge=0)

    width: Optional[int] = None

    height: Optional[int] = None

    duration_seconds: Optional[float] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# Token Usage
# ==============================================================================


class TokenUsage(StudioBaseModel):
    """
    Token usage for LLM requests.
    """

    prompt_tokens: int = Field(default=0, ge=0)

    completion_tokens: int = Field(default=0, ge=0)

    total_tokens: int = Field(default=0, ge=0)


# ==============================================================================
# Cost Information
# ==============================================================================


class CostInfo(StudioBaseModel):
    """
    Estimated generation cost.
    """

    currency: str = "USD"

    estimated_cost: float = Field(default=0.0, ge=0.0)

    actual_cost: Optional[float] = Field(default=None, ge=0.0)


# ==============================================================================
# Main Generation Model
# ==============================================================================


class Generation(StudioBaseModel):
    """
    Represents one AI generation job.
    """

    generation_type: GenerationType

    status: GenerationStatus = GenerationStatus.PENDING

    provider_name: str

    provider_model: Optional[str] = None

    prompt: Prompt

    parameters: GenerationParameters = Field(
        default_factory=GenerationParameters
    )

    result: Optional[GenerationResult] = None

    token_usage: Optional[TokenUsage] = None

    cost: CostInfo = Field(default_factory=CostInfo)

    finish_reason: Optional[FinishReason] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    execution_time_ms: Optional[int] = None

    retry_count: int = Field(default=0, ge=0)

    error_message: Optional[str] = None

    warnings: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        self.status = GenerationStatus.RUNNING
        self.started_at = datetime.now(UTC)
        self.touch()

    def complete(
        self,
        result: GenerationResult,
        finish_reason: FinishReason = FinishReason.SUCCESS,
    ) -> None:
        self.status = GenerationStatus.COMPLETED
        self.result = result
        self.finish_reason = finish_reason
        self.completed_at = datetime.now(UTC)

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(delta.total_seconds() * 1000)

        self.touch()

    def fail(self, message: str) -> None:
        self.status = GenerationStatus.FAILED
        self.error_message = message
        self.completed_at = datetime.now(UTC)
        self.touch()

    def cancel(self) -> None:
        self.status = GenerationStatus.CANCELLED
        self.finish_reason = FinishReason.CANCELLED
        self.completed_at = datetime.now(UTC)
        self.touch()

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
        self.touch()

    @property
    def is_finished(self) -> bool:
        return self.status in {
            GenerationStatus.COMPLETED,
            GenerationStatus.FAILED,
            GenerationStatus.CANCELLED,
        }

    @property
    def succeeded(self) -> bool:
        return self.status == GenerationStatus.COMPLETED

    @property
    def failed(self) -> bool:
        return self.status == GenerationStatus.FAILED