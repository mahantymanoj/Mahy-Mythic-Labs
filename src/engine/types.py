"""
src/engine/types.py

Shared engine types for Mahy Mythic Labs Studio OS.

This module contains shared enums and dataclasses used by the
workflow engine. It intentionally contains NO business logic.

Python
------
>=3.11
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from src.agents.base_agent import AgentResult
from src.engine.context import EngineContext


# ==============================================================================
# Workflow Stage
# ==============================================================================


class WorkflowStage(str, Enum):
    """
    Canonical Studio OS workflow stages.
    """

    RESEARCH = "research"

    SCRIPT = "script"

    STORYBOARD = "storyboard"

    IMAGE = "image"

    VIDEO = "video"

    NARRATION = "narration"

    QUALITY = "quality"

    SEO = "seo"

    PUBLISHING = "publishing"


# ==============================================================================
# Director Status
# ==============================================================================


class DirectorStatus(str, Enum):
    """
    Director execution state.
    """

    IDLE = "idle"

    INITIALIZING = "initializing"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ==============================================================================
# Workflow Definition
# ==============================================================================


@dataclass(slots=True)
class WorkflowDefinition:
    """
    One executable workflow stage.
    """

    stage: WorkflowStage

    enabled: bool = True

    timeout: int | None = None

    retry_count: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Director Hooks
# ==============================================================================


@dataclass(slots=True)
class DirectorHooks:
    """
    Lifecycle callbacks.
    """

    before_workflow: Callable[..., Any] | None = None

    after_workflow: Callable[..., Any] | None = None

    before_stage: Callable[..., Any] | None = None

    after_stage: Callable[..., Any] | None = None

    # ==============================================================================
# Director Configuration
# ==============================================================================


@dataclass(slots=True)
class DirectorConfig:
    """
    Global workflow execution configuration.
    """

    stop_on_failure: bool = True

    publish_events: bool = True

    auto_initialize_agents: bool = True

    stage_timeout: int = 600

    max_retries: int = 1

    checkpoint_enabled: bool = False

    checkpoint_directory: str = ".studio/checkpoints"

    allow_parallel_execution: bool = True

    validate_workflow_before_run: bool = True

    collect_metrics: bool = True

    emit_statistics: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Workflow Statistics
# ==============================================================================


@dataclass(slots=True)
class WorkflowStatistics:
    """
    Runtime workflow statistics.
    """

    total_stages: int = 0

    completed_stages: int = 0

    failed_stages: int = 0

    skipped_stages: int = 0

    cancelled_stages: int = 0

    total_duration_seconds: float = 0.0

    average_stage_duration: float = 0.0

    success_rate: float = 100.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Stage Execution Summary
# ==============================================================================


@dataclass(slots=True)
class StageExecutionSummary:
    """
    Execution information for a single stage.
    """

    stage: WorkflowStage

    success: bool

    attempts: int = 1

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Execution Checkpoint
# ==============================================================================


@dataclass(slots=True)
class ExecutionCheckpoint:
    """
    Serializable workflow checkpoint.
    """

    workflow_id: str

    execution_id: str

    current_stage: WorkflowStage | None = None

    completed_stages: list[
        WorkflowStage
    ] = field(
        default_factory=list
    )

    failed_stages: list[
        WorkflowStage
    ] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    context_snapshot: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Director Result
# ==============================================================================


@dataclass(slots=True)
class DirectorResult:
    """
    Result returned by Director.run().
    """

    success: bool

    workflow_id: str

    execution_id: str

    status: DirectorStatus

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    completed_stages: list[
        WorkflowStage
    ] = field(
        default_factory=list
    )

    failed_stage: WorkflowStage | None = None

    stage_results: dict[
        WorkflowStage,
        AgentResult,
    ] = field(
        default_factory=dict
    )

    statistics: WorkflowStatistics | None = None

    context: EngineContext | None = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Constants
# ==============================================================================


DEFAULT_WORKFLOW_NAME = "Mahy Mythic Labs Workflow"

DEFAULT_WORKFLOW_VERSION = "1.0.0"

ENGINE_VERSION = "1.0.0"