"""
src/models/generation.py

Domain models for AI generation requests.

This module defines the core models representing an AI generation
lifecycle within Mahy Mythic Labs Studio OS.

A Generation represents a single invocation of an AI provider
(OpenAI, Anthropic, Gemini, Runway, Kling, Veo, Flux, etc.)
regardless of the generated content type.

Examples
--------
Image Generation
Video Generation
Audio Generation
Voice Generation
Music Generation
Research Generation
Script Generation
Subtitle Generation

Relationships
-------------
Project
    └── Episode
            └── Scene
                    └── Shot
                            └── Generation
                                    └── Asset

Notes
-----
This module contains ONLY domain models.

Provider-specific logic belongs to:

    src/providers/

Author
------
Mahy Mythic Labs

Python
------
>=3.11

Pydantic
---------
>=2.x
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID
from pydantic import Field, field_validator
from .base import EntityModel, ValueModel
from .components.prompt import PromptSet
from .metadata import CostInfo, TokenUsage

# ==============================================================================
# Enumerations
# ==============================================================================


class GenerationType(str, Enum):
    """
    Supported AI generation types.
    """

    TEXT = "text"

    IMAGE = "image"

    VIDEO = "video"

    AUDIO = "audio"

    VOICE = "voice"

    MUSIC = "music"

    SCRIPT = "script"

    RESEARCH = "research"

    THUMBNAIL = "thumbnail"

    SUBTITLE = "subtitle"

    EMBEDDING = "embedding"


class GenerationStatus(str, Enum):
    """
    Current lifecycle state.
    """

    PENDING = "pending"

    QUEUED = "queued"

    RUNNING = "running"

    RETRYING = "retrying"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class FinishReason(str, Enum):
    """
    Final completion reason.
    """

    SUCCESS = "success"

    STOP = "stop"

    LENGTH = "length"

    ERROR = "error"

    CANCELLED = "cancelled"

    CONTENT_FILTER = "content_filter"

    UNKNOWN = "unknown"


class GenerationPriority(str, Enum):
    """
    Scheduler priority.
    """

    LOW = "low"

    NORMAL = "normal"

    HIGH = "high"

    URGENT = "urgent"


# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_MAX_RETRIES = 3

DEFAULT_CURRENCY = "USD"

DEFAULT_PROGRESS = 0

# ==============================================================================
# Generation Parameters
# ==============================================================================


class GenerationParameters(ValueModel):
    """
    Configuration supplied to the AI provider.

    These values describe HOW the content should be generated,
    independent of the provider implementation.
    """

    model_name: str | None = Field(
        default=None,
        description="AI model identifier.",
    )

    model_version: str | None = Field(
        default=None,
        description="Model version.",
    )

    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature.",
    )

    top_p: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling value.",
    )

    seed: int | None = Field(
        default=None,
        description="Random generation seed.",
    )

    width: int | None = Field(
        default=None,
        ge=1,
        description="Output width.",
    )

    height: int | None = Field(
        default=None,
        ge=1,
        description="Output height.",
    )

    aspect_ratio: str | None = Field(
        default=None,
        description="Aspect ratio (16:9, 9:16, 1:1...).",
    )

    fps: int | None = Field(
        default=None,
        ge=1,
        description="Frames per second.",
    )

    duration_seconds: float | None = Field(
        default=None,
        ge=0,
        description="Generated duration.",
    )

    quality: str | None = Field(
        default=None,
        description="Requested quality level.",
    )

    cfg_scale: float | None = Field(
        default=None,
        ge=0,
        description="CFG scale for diffusion models.",
    )

    steps: int | None = Field(
        default=None,
        ge=1,
        description="Sampling steps.",
    )

    extra: dict[str, object] = Field(
        default_factory=dict,
        description="Provider-specific parameters.",
    )


# ==============================================================================
# Generation Result
# ==============================================================================


class GenerationResult(ValueModel):
    """
    Output returned from an AI provider.
    """

    output_text: str | None = Field(
        default=None,
        description="Generated text.",
    )

    output_uri: str | None = Field(
        default=None,
        description="Primary output location.",
    )

    preview_uri: str | None = Field(
        default=None,
        description="Preview image/video/audio.",
    )

    thumbnail_uri: str | None = Field(
        default=None,
        description="Thumbnail URI.",
    )

    mime_type: str | None = Field(
        default=None,
        description="Output MIME type.",
    )

    checksum: str | None = Field(
        default=None,
        description="Content checksum.",
    )

    file_size_bytes: int | None = Field(
        default=None,
        ge=0,
        description="Output file size.",
    )

    width: int | None = Field(
        default=None,
        ge=1,
        description="Output width.",
    )

    height: int | None = Field(
        default=None,
        ge=1,
        description="Output height.",
    )

    duration_seconds: float | None = Field(
        default=None,
        ge=0,
        description="Output duration.",
    )

    metadata: dict[str, object] = Field(
        default_factory=dict,
        description="Provider metadata.",
    )

# ==============================================================================
# Generation Entity
# ==============================================================================


class Generation(EntityModel):
    """
    Represents a single AI generation request.

    A Generation tracks the complete lifecycle of an AI request,
    from submission through completion or failure.

    This model is provider-agnostic and can represent requests to
    OpenAI, Anthropic, Google, Runway, Kling, Flux, Veo, and
    future providers.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    project_id: UUID | None = Field(
        default=None,
        description="Associated project.",
    )

    episode_id: UUID | None = Field(
        default=None,
        description="Associated episode.",
    )

    scene_id: UUID | None = Field(
        default=None,
        description="Associated scene.",
    )

    shot_id: UUID | None = Field(
        default=None,
        description="Associated shot.",
    )

    asset_id: UUID | None = Field(
        default=None,
        description="Generated asset identifier.",
    )

    # ------------------------------------------------------------------
    # Request Information
    # ------------------------------------------------------------------

    generation_type: GenerationType = Field(
        description="Type of generation.",
    )

    priority: GenerationPriority = Field(
        default=GenerationPriority.NORMAL,
        description="Scheduling priority.",
    )

    status: GenerationStatus = Field(
        default=GenerationStatus.PENDING,
        description="Current lifecycle status.",
    )

    provider_name: str = Field(
        min_length=1,
        description="Provider name.",
    )

    provider_model: str | None = Field(
        default=None,
        description="Provider model.",
    )

    provider_request_id: str | None = Field(
        default=None,
        description="Provider job/request identifier.",
    )

    # ------------------------------------------------------------------
    # Prompt & Parameters
    # ------------------------------------------------------------------

    prompt: PromptSet = Field(
        description="Generation prompt.",
    )

    parameters: GenerationParameters = Field(
        default_factory=GenerationParameters,
    )

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    result: GenerationResult | None = Field(
        default=None,
    )

    # ------------------------------------------------------------------
    # Usage & Cost
    # ------------------------------------------------------------------

    token_usage: TokenUsage | None = Field(
        default=None,
    )

    cost: CostInfo | None = Field(
        default=None,
    )

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------

    retry_count: int = Field(
        default=0,
        ge=0,
    )

    max_retries: int = Field(
        default=DEFAULT_MAX_RETRIES,
        ge=0,
    )

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------

    progress: int = Field(
        default=DEFAULT_PROGRESS,
        ge=0,
        le=100,
    )

    finish_reason: FinishReason | None = Field(
        default=None,
    )

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    queued_at: datetime | None = Field(
        default=None,
    )

    started_at: datetime | None = Field(
        default=None,
    )

    completed_at: datetime | None = Field(
        default=None,
    )

    execution_time_ms: int | None = Field(
        default=None,
        ge=0,
    )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    error_message: str | None = Field(
        default=None,
    )

    warnings: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("provider_name")
    @classmethod
    def validate_provider_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Provider name cannot be empty."
            )

        return value


    @field_validator("progress")
    @classmethod
    def validate_progress(cls, value: int) -> int:

        if not 0 <= value <= 100:
            raise ValueError(
                "Progress must be between 0 and 100."
            )

        return value


    @field_validator("retry_count")
    @classmethod
    def validate_retry_count(
        cls,
        value: int,
    ) -> int:

        if value < 0:
            raise ValueError(
                "Retry count cannot be negative."
            )

        return value

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Business Validation
    # ------------------------------------------------------------------

    def validate_state(self) -> None:
        """
        Validate business rules.
        """

        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValueError(
                "completed_at cannot be earlier than started_at."
            )

        if self.retry_count > self.max_retries:
            raise ValueError(
                "Retry count exceeded maximum retries."
            )

    def queue(self) -> None:
        """
        Mark the generation as queued.
        """
        self.status = GenerationStatus.QUEUED
        self.queued_at = datetime.now(UTC)
        self.touch()

    def start(self) -> None:
        """
        Start generation.
        """
        self.status = GenerationStatus.RUNNING
        self.started_at = datetime.now(UTC)
        self.progress = 0
        self.touch()

    def complete(
        self,
        result: GenerationResult,
        finish_reason: FinishReason = FinishReason.SUCCESS,
    ) -> None:
        """
        Complete the generation successfully.
        """
        self.status = GenerationStatus.COMPLETED
        self.result = result
        self.finish_reason = finish_reason
        self.progress = 100
        self.completed_at = datetime.now(UTC)

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(
                delta.total_seconds() * 1000
            )

        self.validate_state()
        self.touch()

    def fail(
        self,
        message: str,
    ) -> None:
        """
        Mark generation as failed.
        """
        self.status = GenerationStatus.FAILED
        self.error_message = message
        self.finish_reason = FinishReason.ERROR
        self.completed_at = datetime.now(UTC)

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(
                delta.total_seconds() * 1000
            )

        self.validate_state()
        self.touch()

    def cancel(self) -> None:
        """
        Cancel generation.
        """
        self.status = GenerationStatus.CANCELLED
        self.finish_reason = FinishReason.CANCELLED
        self.completed_at = datetime.now(UTC)
        self.validate_state()
        self.touch()

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------

    def can_retry(self) -> bool:
        """
        Return True if another retry is allowed.
        """
        return self.retry_count < self.max_retries

    def retry(self) -> None:
        """
        Reset the generation for another attempt.
        """
        if not self.can_retry():
            raise RuntimeError(
                "Maximum retry count exceeded."
            )

        self.retry_count += 1
        self.status = GenerationStatus.RETRYING
        self.progress = 0
        self.error_message = None
        self.finish_reason = None
        self.started_at = None
        self.completed_at = None
        self.execution_time_ms = None
        self.result = None

        self.validate_state()
        self.touch()

    def reset(self) -> None:
        """
        Reset generation to its initial state.
        """
        self.status = GenerationStatus.PENDING
        self.progress = 0
        self.retry_count = 0
        self.error_message = None
        self.finish_reason = None
        self.started_at = None
        self.completed_at = None
        self.execution_time_ms = None
        self.result = None

        self.validate_state()
        self.touch()

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------

    def update_progress(
        self,
        value: int,
    ) -> None:
        """
        Update generation progress.

        Parameters
        ----------
        value
            Progress percentage (0-100).
        """
        self.progress = max(0, min(100, value))
        self.touch()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def add_warning(
        self,
        warning: str,
    ) -> None:
        """
        Add a warning message.
        """
        self.warnings.append(warning)
        self.touch()

    def clear_error(self) -> None:
        """
        Clear the current error.
        """
        self.error_message = None
        self.touch()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_pending(self) -> bool:
        return self.status == GenerationStatus.PENDING

    @property
    def is_queued(self) -> bool:
        return self.status == GenerationStatus.QUEUED

    @property
    def is_running(self) -> bool:
        return self.status in {
            GenerationStatus.RUNNING,
            GenerationStatus.RETRYING,
        }

    @property
    def is_completed(self) -> bool:
        return self.status == GenerationStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == GenerationStatus.FAILED

    @property
    def is_cancelled(self) -> bool:
        return self.status == GenerationStatus.CANCELLED

    @property
    def is_finished(self) -> bool:
        return self.status in {
            GenerationStatus.COMPLETED,
            GenerationStatus.FAILED,
            GenerationStatus.CANCELLED,
        }

    @property
    def duration(self) -> float | None:
        """
        Execution duration in seconds.
        """
        if self.started_at is None:
            return None

        end_time = self.completed_at or datetime.now(UTC)
        return (end_time - self.started_at).total_seconds()

    @property
    def has_result(self) -> bool:
        return self.result is not None

    @property
    def has_error(self) -> bool:
        return self.error_message is not None

    @property
    def execution_seconds(self) -> float | None:
        """
        Execution time in seconds.
        """

        if self.execution_time_ms is None:
            return None

        return self.execution_time_ms / 1000

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.provider_name}/"
            f"{self.generation_type.value}"
            f" ({self.status.value})"
    )

    def __repr__(self) -> str:
        return (
            "Generation("
            f"id={self.id}, "
            f"type={self.generation_type.value}, "
            f"status={self.status.value}, "
            f"provider={self.provider_name}"
            ")"
        )