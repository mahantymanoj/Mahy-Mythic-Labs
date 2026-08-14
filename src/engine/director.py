"""
src/engine/director.py

Enterprise Workflow Director for Mahy Mythic Labs Studio OS.

The Director is responsible for orchestrating the complete
content production pipeline. It coordinates agents,
manages execution order, publishes events and maintains
workflow state through EngineContext.

This class is NOT an AI agent.

Responsibilities
----------------
- Register workflow stages
- Register agents
- Execute production pipeline
- Retry failed stages
- Publish workflow events
- Manage execution state
- Track metrics
- Produce final workflow result

Python
------
>=3.11
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.agents.base_agent import (
    AgentResult,
)

from src.engine.context import (
    EngineContext,
    StageResult,
)

from src.engine.events import (
    EventBus,
    EventPriority,
    EventType,
    get_event_bus,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# Workflow Stage
# ==============================================================================


class WorkflowStage(str, Enum):
    """
    Standard Studio OS workflow stages.
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
    Current workflow execution status.
    """

    IDLE = "idle"

    INITIALIZING = "initializing"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ==============================================================================
# Stage Definition
# ==============================================================================


@dataclass(slots=True)
class WorkflowDefinition:
    """
    Defines a workflow stage.
    """

    stage: WorkflowStage

    description: str = ""

    enabled: bool = True

    retry_count: int = 0

    timeout: int | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Director Configuration
# ==============================================================================


@dataclass(slots=True)
class DirectorConfig:
    """
    Runtime configuration for the Director.
    """

    max_retries: int = 1

    stage_timeout: int = 900

    stop_on_failure: bool = True

    publish_events: bool = True

    collect_metrics: bool = True

    continue_on_warning: bool = True

    auto_save_context: bool = False

    checkpoint_directory: str = "runtime/checkpoints"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Director Result
# ==============================================================================


@dataclass(slots=True)
class DirectorResult:
    """
    Final workflow execution result.
    """

    success: bool

    workflow_id: str

    execution_id: str

    status: DirectorStatus

    started_at: datetime

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    completed_stages: list[WorkflowStage] = field(
        default_factory=list
    )

    failed_stage: WorkflowStage | None = None

    stage_results: dict[
        WorkflowStage,
        AgentResult,
    ] = field(
        default_factory=dict
    )

    context: EngineContext | None = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Director Hooks
# ==============================================================================


@dataclass(slots=True)
class DirectorHooks:
    """
    Lifecycle callbacks executed by the Director.
    All callbacks are optional.
    """

    before_workflow: Any | None = None

    after_workflow: Any | None = None

    before_stage: Any | None = None

    after_stage: Any | None = None

    on_failure: Any | None = None

    on_cancel: Any | None = None


# ==============================================================================
# Director
# ==============================================================================


class Director:
    """
    Enterprise workflow orchestration engine.

    The Director coordinates every production stage and is the
    execution backbone of Studio OS.

    Typical workflow:

        Research
            ↓
        Script
            ↓
        Storyboard
            ↓
        Image
            ↓
        Video
            ↓
        Narration
            ↓
        Quality
            ↓
        SEO
            ↓
        Publishing

    """

    def __init__(
        self,
        *,
        context: EngineContext | None = None,
        config: DirectorConfig | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        """
        Initialize the workflow director.
        """

        self.context = context or EngineContext()

        self.config = config or DirectorConfig()

        self.event_bus = (
            event_bus
            or get_event_bus()
        )

        self.status = DirectorStatus.IDLE

        self.execution_id: str | None = None

        self.started_at: datetime | None = None

        self.completed_at: datetime | None = None

        self._cancel_requested = False

        self._paused = False

        self.hooks = DirectorHooks()

        # ----------------------------------------------------------
        # Agent Registry
        # ----------------------------------------------------------

        self._agents: dict[
            WorkflowStage,
            Any,
        ] = {}

        # ----------------------------------------------------------
        # Workflow Definition
        # ----------------------------------------------------------

        self._workflow: list[
            WorkflowDefinition
        ] = []

        self._register_default_workflow()

    # ==================================================================
    # Workflow Registration
    # ==================================================================

    def _register_default_workflow(
        self,
    ) -> None:
        """
        Register the default Studio OS workflow.
        """

        self._workflow = [

            WorkflowDefinition(
                WorkflowStage.RESEARCH,
                description="Research topic",
            ),

            WorkflowDefinition(
                WorkflowStage.SCRIPT,
                description="Generate script",
            ),

            WorkflowDefinition(
                WorkflowStage.STORYBOARD,
                description="Generate storyboard",
            ),

            WorkflowDefinition(
                WorkflowStage.IMAGE,
                description="Generate images",
            ),

            WorkflowDefinition(
                WorkflowStage.VIDEO,
                description="Generate video",
            ),

            WorkflowDefinition(
                WorkflowStage.NARRATION,
                description="Generate narration",
            ),

            WorkflowDefinition(
                WorkflowStage.QUALITY,
                description="Quality validation",
            ),

            WorkflowDefinition(
                WorkflowStage.SEO,
                description="SEO generation",
            ),

            WorkflowDefinition(
                WorkflowStage.PUBLISHING,
                description="Publishing",
            ),
        ]

    # ==================================================================
    # Agent Registration
    # ==================================================================

    def register_agent(
        self,
        stage: WorkflowStage,
        agent: Any,
    ) -> None:
        """
        Register an agent for a workflow stage.
        """

        self._agents[stage] = agent

        logger.info(
            "Registered %s -> %s",
            stage.value,
            agent.__class__.__name__,
        )

    def unregister_agent(
        self,
        stage: WorkflowStage,
    ) -> None:
        """
        Remove an agent.
        """

        self._agents.pop(
            stage,
            None,
        )

    def get_agent(
        self,
        stage: WorkflowStage,
    ) -> Any | None:
        """
        Return the registered agent.
        """

        return self._agents.get(stage)

    def has_agent(
        self,
        stage: WorkflowStage,
    ) -> bool:
        """
        Return True if an agent exists.
        """

        return stage in self._agents

    @property
    def registered_agents(
        self,
    ) -> dict[WorkflowStage, Any]:
        """
        Return a copy of the agent registry.
        """

        return dict(self._agents)

    # ==================================================================
    # Workflow Management
    # ==================================================================

    def workflow(
        self,
    ) -> list[WorkflowDefinition]:
        """
        Return workflow definition.
        """

        return list(self._workflow)

    def add_stage(
        self,
        definition: WorkflowDefinition,
    ) -> None:
        """
        Append a workflow stage.
        """

        self._workflow.append(definition)

    def remove_stage(
        self,
        stage: WorkflowStage,
    ) -> None:
        """
        Remove a workflow stage.
        """

        self._workflow = [
            item
            for item in self._workflow
            if item.stage != stage
        ]

    def enable_stage(
        self,
        stage: WorkflowStage,
    ) -> None:
        """
        Enable execution of a stage.
        """

        for item in self._workflow:

            if item.stage == stage:
                item.enabled = True
                return

    def disable_stage(
        self,
        stage: WorkflowStage,
    ) -> None:
        """
        Disable execution of a stage.
        """

        for item in self._workflow:

            if item.stage == stage:
                item.enabled = False
                return

    def stage_definition(
        self,
        stage: WorkflowStage,
    ) -> WorkflowDefinition | None:
        """
        Return workflow definition for a stage.
        """

        for item in self._workflow:

            if item.stage == stage:
                return item

        return None

    # ==================================================================
    # Status Helpers
    # ==================================================================

    @property
    def is_running(
        self,
    ) -> bool:
        return self.status == DirectorStatus.RUNNING

    @property
    def is_completed(
        self,
    ) -> bool:
        return self.status == DirectorStatus.COMPLETED

    @property
    def is_failed(
        self,
    ) -> bool:
        return self.status == DirectorStatus.FAILED

    @property
    def is_cancelled(
        self,
    ) -> bool:
        return self.status == DirectorStatus.CANCELLED

        # ==================================================================
    # Workflow Execution
    # ==================================================================

    async def run(self) -> DirectorResult:
        """
        Execute the complete workflow.
        """

        self.status = DirectorStatus.RUNNING
        self.execution_id = str(uuid.uuid4())

        self.started_at = datetime.now(
            timezone.utc
        )

        self.context.start_workflow()

        workflow_start = time.perf_counter()

        stage_results: dict[
            WorkflowStage,
            AgentResult,
        ] = {}

        completed: list[
            WorkflowStage
        ] = []

        failed_stage: WorkflowStage | None = None

        error_message: str | None = None

        try:

            if self.config.publish_events:
                await self.event_bus.emit(
                    EventType.WORKFLOW_STARTED,
                    source="Director",
                    payload={
                        "workflow_id": self.context.workflow_id,
                        "execution_id": self.execution_id,
                    },
                )

            if self.hooks.before_workflow:
                await self._call_hook(
                    self.hooks.before_workflow,
                )

            for definition in self._workflow:

                if self._cancel_requested:
                    raise asyncio.CancelledError()

                if not definition.enabled:
                    continue

                result = await self._execute_stage(
                    definition,
                )

                stage_results[
                    definition.stage
                ] = result

                if result.success:

                    completed.append(
                        definition.stage
                    )

                else:

                    failed_stage = (
                        definition.stage
                    )

                    error_message = (
                        result.error
                    )

                    if self.config.stop_on_failure:
                        raise RuntimeError(
                            result.error
                        )

            self.status = (
                DirectorStatus.COMPLETED
            )

            self.context.complete_workflow()

        except asyncio.CancelledError:

            self.status = (
                DirectorStatus.CANCELLED
            )

            self.context.fail_workflow(
                "Workflow cancelled."
            )

            raise

        except Exception as exc:

            self.status = (
                DirectorStatus.FAILED
            )

            self.context.fail_workflow(
                str(exc)
            )

            error_message = str(exc)

            logger.exception(
                "Workflow failed."
            )

        finally:

            self.completed_at = (
                datetime.now(
                    timezone.utc
                )
            )

            duration = (
                time.perf_counter()
                - workflow_start
            )

            if self.hooks.after_workflow:

                await self._call_hook(
                    self.hooks.after_workflow,
                )

            if self.config.publish_events:

                event = (
                    EventType.WORKFLOW_COMPLETED
                    if self.status
                    == DirectorStatus.COMPLETED
                    else EventType.WORKFLOW_FAILED
                )

                await self.event_bus.emit(
                    event,
                    source="Director",
                    payload={
                        "workflow_id": self.context.workflow_id,
                        "execution_id": self.execution_id,
                        "status": self.status.value,
                    },
                )

        return DirectorResult(
            success=(
                self.status
                == DirectorStatus.COMPLETED
            ),
            workflow_id=self.context.workflow_id,
            execution_id=self.execution_id,
            status=self.status,
            started_at=self.started_at,
            completed_at=self.completed_at,
            duration_seconds=duration,
            completed_stages=completed,
            failed_stage=failed_stage,
            stage_results=stage_results,
            context=self.context,
            error=error_message,
        )

    # ==================================================================
    # Stage Execution
    # ==================================================================

    async def _execute_stage(
        self,
        definition: WorkflowDefinition,
    ) -> AgentResult:
        """
        Execute one workflow stage.
        """

        self.context.set_current_stage(
            definition.stage.value
        )

        agent = self.get_agent(
            definition.stage
        )

        if agent is None:

            raise RuntimeError(
                f"No agent registered for "
                f"{definition.stage.value}"
            )

        retries = max(
            definition.retry_count,
            self.config.max_retries,
        )

        last_result: AgentResult | None = None

        for attempt in range(
            retries + 1
        ):

            try:

                if (
                    self.hooks.before_stage
                ):
                    await self._call_hook(
                        self.hooks.before_stage,
                        definition.stage,
                    )

                if self.config.publish_events:

                    await self.event_bus.emit(
                        EventType.AGENT_STARTED,
                        source=definition.stage.value,
                    )

                result = await asyncio.wait_for(
                    agent.run(
                        context=self.context,
                    ),
                    timeout=(
                        definition.timeout
                        or self.config.stage_timeout
                    ),
                )

                last_result = result

                if result.success:

                    self.context.set_stage_result(
                        result=StageResult(
                            stage=definition.stage.value,
                            success=result.success,
                            output=result.output,
                        ),
                    )

                    self.context.set_output(
                        definition.stage.value,
                        result.output,
                    )

                    if (
                        self.hooks.after_stage
                    ):
                        await self._call_hook(
                            self.hooks.after_stage,
                            definition.stage,
                            result,
                        )

                    return result

                logger.warning(
                    "Stage %s failed "
                    "(attempt %d/%d)",
                    definition.stage.value,
                    attempt + 1,
                    retries + 1,
                )

            except Exception as exc:

                logger.exception(
                    "Stage execution failed: %s",
                    definition.stage.value,
                )

                last_result = AgentResult(
                    success=False,
                    agent=agent.agent_type,
                    error=str(exc),
                )

        return last_result

        # ==================================================================
    # Hooks
    # ==================================================================

    async def _call_hook(
        self,
        hook: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Execute a lifecycle hook.

        Supports both synchronous and asynchronous callables.
        """

        if hook is None:
            return

        try:

            if asyncio.iscoroutinefunction(hook):
                await hook(*args, **kwargs)
                return

            result = hook(*args, **kwargs)

            if asyncio.iscoroutine(result):
                await result

        except Exception:

            logger.exception(
                "Director hook failed."
            )

    # ==================================================================
    # Cancellation
    # ==================================================================

    def cancel(self) -> None:
        """
        Request workflow cancellation.

        The currently executing stage is allowed to finish.
        """

        self._cancel_requested = True

        logger.warning(
            "Workflow cancellation requested."
        )

    @property
    def cancellation_requested(
        self,
    ) -> bool:
        """
        Return True when cancellation has been requested.
        """

        return self._cancel_requested

    # ==================================================================
    # Pause / Resume
    # ==================================================================

    def pause(self) -> None:
        """
        Pause workflow execution.
        """

        if self.status != DirectorStatus.RUNNING:
            return

        self._paused = True

        self.status = DirectorStatus.PAUSED

        logger.info(
            "Workflow paused."
        )

    def resume(self) -> None:
        """
        Resume workflow execution.
        """

        if self.status != DirectorStatus.PAUSED:
            return

        self._paused = False

        self.status = DirectorStatus.RUNNING

        logger.info(
            "Workflow resumed."
        )

    @property
    def is_paused(
        self,
    ) -> bool:
        return self._paused

    async def _wait_if_paused(
        self,
    ) -> None:
        """
        Suspend execution while paused.
        """

        while self._paused:

            await asyncio.sleep(
                0.25
            )

    # ==================================================================
    # Progress
    # ==================================================================

    @property
    def total_stages(
        self,
    ) -> int:
        """
        Number of enabled workflow stages.
        """

        return sum(
            1
            for stage in self._workflow
            if stage.enabled
        )

    @property
    def completed_stage_count(
        self,
    ) -> int:
        """
        Number of successfully completed stages.
        """

        return self.context.completed_stage_count

    @property
    def progress(
        self,
    ) -> float:
        """
        Workflow progress percentage.
        """

        total = self.total_stages

        if total == 0:
            return 0.0

        return (
            self.completed_stage_count
            / total
        ) * 100.0

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Runtime workflow statistics.
        """

        return {

            "workflow_id":
                self.context.workflow_id,

            "execution_id":
                self.execution_id,

            "status":
                self.status.value,

            "progress":
                round(
                    self.progress,
                    2,
                ),

            "completed_stages":
                self.completed_stage_count,

            "total_stages":
                self.total_stages,

            "artifacts":
                self.context.artifact_count,

            "events":
                self.context.event_count,

            "metrics":
                self.context.metric_count,

            "outputs":
                self.context.output_count,

            "variables":
                self.context.variable_count,
        }

    # ==================================================================
    # Context Checkpoints
    # ==================================================================

    def save_checkpoint(
        self,
        path: str,
    ) -> None:
        """
        Save the current workflow context.
        """

        self.context.save(path)

        logger.info(
            "Checkpoint saved: %s",
            path,
        )

    def load_checkpoint(
        self,
        path: str,
    ) -> None:
        """
        Restore a workflow context.
        """

        self.context = EngineContext.load(
            path
        )

        logger.info(
            "Checkpoint loaded: %s",
            path,
        )

    # ==================================================================
    # Reset
    # ==================================================================

    def reset(
        self,
    ) -> None:
        """
        Reset the director for another workflow execution.
        """

        self.status = DirectorStatus.IDLE

        self.execution_id = None

        self.started_at = None

        self.completed_at = None

        self._cancel_requested = False

        self._paused = False

        self.context.clear()

    # ==================================================================
    # Representation
    # ==================================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"status={self.status.value!r}, "
            f"progress={self.progress:.1f}%, "
            f"agents={len(self._agents)}, "
            f"stages={self.total_stages})"
        )

        # ==================================================================
    # Agent Lifecycle
    # ==================================================================

    async def initialize_agents(self) -> None:
        """
        Initialize all registered agents.
        """

        logger.info("Initializing agents...")

        for stage, agent in self._agents.items():

            try:

                if hasattr(agent, "initialize"):
                    await agent.initialize(
                        context=self.context,
                    )

                logger.info(
                    "Initialized agent: %s",
                    stage.value,
                )

            except Exception:

                logger.exception(
                    "Failed to initialize %s",
                    stage.value,
                )

                raise

    async def close_agents(self) -> None:
        """
        Gracefully close every registered agent.
        """

        logger.info("Closing agents...")

        for stage, agent in self._agents.items():

            try:

                if hasattr(agent, "close"):
                    await agent.close()

            except Exception:

                logger.exception(
                    "Error closing %s",
                    stage.value,
                )

    # ==================================================================
    # Validation
    # ==================================================================

    def validate_workflow(self) -> None:
        """
        Ensure every enabled workflow stage has a registered agent.
        """

        missing: list[str] = []

        for definition in self._workflow:

            if not definition.enabled:
                continue

            if definition.stage not in self._agents:
                missing.append(
                    definition.stage.value
                )

        if missing:

            raise RuntimeError(
                "Missing agents: "
                + ", ".join(missing)
            )

    def health_check(self) -> dict[str, bool]:
        """
        Return health information for every stage.
        """

        report: dict[str, bool] = {}

        for definition in self._workflow:

            report[
                definition.stage.value
            ] = (
                definition.stage
                in self._agents
            )

        return report

    # ==================================================================
    # Workflow Editing
    # ==================================================================

    def insert_stage(
        self,
        index: int,
        definition: WorkflowDefinition,
    ) -> None:
        """
        Insert a stage into the workflow.
        """

        self._workflow.insert(
            index,
            definition,
        )

    def move_stage(
        self,
        stage: WorkflowStage,
        new_index: int,
    ) -> None:
        """
        Move a workflow stage.
        """

        for i, item in enumerate(
            self._workflow
        ):

            if item.stage == stage:

                definition = self._workflow.pop(i)

                self._workflow.insert(
                    new_index,
                    definition,
                )

                return

    def clear_workflow(self) -> None:
        """
        Remove every stage.
        """

        self._workflow.clear()

    # ==================================================================
    # Agent Utilities
    # ==================================================================

    def registered_stage_names(
        self,
    ) -> list[str]:
        """
        Return registered stage names.
        """

        return [
            stage.value
            for stage in self._agents
        ]

    def registered_agent_names(
        self,
    ) -> list[str]:
        """
        Return registered agent class names.
        """

        return [
            agent.__class__.__name__
            for agent in self._agents.values()
        ]

    # ==================================================================
    # Workflow Summary
    # ==================================================================

    def summary(self) -> dict[str, Any]:
        """
        Return a high-level workflow summary.
        """

        return {
            "workflow_id": self.context.workflow_id,
            "status": self.status.value,
            "progress": round(
                self.progress,
                2,
            ),
            "agents": self.registered_agent_names(),
            "stages": [
                stage.stage.value
                for stage in self._workflow
            ],
            "statistics": self.statistics(),
        }

    # ==================================================================
    # Event Helpers
    # ==================================================================

    async def publish_info(
        self,
        message: str,
    ) -> None:
        """
        Publish an informational workflow event.
        """

        if not self.config.publish_events:
            return

        await self.event_bus.emit(
            EventType.INFO,
            source="Director",
            payload={
                "message": message,
            },
            priority=EventPriority.NORMAL,
        )

    async def publish_warning(
        self,
        message: str,
    ) -> None:
        """
        Publish a warning event.
        """

        if not self.config.publish_events:
            return

        await self.event_bus.emit(
            EventType.WARNING,
            source="Director",
            payload={
                "message": message,
            },
            priority=EventPriority.HIGH,
        )

    async def publish_error(
        self,
        message: str,
    ) -> None:
        """
        Publish an error event.
        """

        if not self.config.publish_events:
            return

        await self.event_bus.emit(
            EventType.ERROR,
            source="Director",
            payload={
                "message": message,
            },
            priority=EventPriority.CRITICAL,
        )

    # ==================================================================
    # Async Context Manager
    # ==================================================================

    async def __aenter__(
        self,
    ) -> "Director":
        """
        Async context manager entry.
        """

        await self.initialize_agents()

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        """
        Async context manager exit.
        """

        await self.close_agents()
    
