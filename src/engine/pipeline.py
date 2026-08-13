"""
src/engine/pipeline.py

Enterprise Pipeline Engine for Mahy Mythic Labs Studio OS.

A Pipeline is the highest-level orchestration unit.

Hierarchy
---------
Pipeline
    └── Workflow(s)
            └── Director
                    └── Agents

Python
------
>=3.11
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import logging
import uuid

from src.engine.workflow import Workflow

logger = logging.getLogger(__name__)


# ==============================================================================
# Pipeline Status
# ==============================================================================


class PipelineStatus(str, Enum):
    """
    Runtime status of a pipeline.
    """

    IDLE = "idle"

    INITIALIZING = "initializing"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ==============================================================================
# Pipeline Stage
# ==============================================================================


@dataclass(slots=True)
class PipelineStage:
    """
    One workflow inside a pipeline.
    """

    name: str

    workflow: Workflow

    enabled: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Pipeline Result
# ==============================================================================


@dataclass(slots=True)
class PipelineResult:
    """
    Final pipeline execution result.
    """

    success: bool

    pipeline_id: str

    execution_id: str

    status: PipelineStatus

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    completed_workflows: list[str] = field(
        default_factory=list
    )

    failed_workflow: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Pipeline
# ==============================================================================


class Pipeline:
    """
    Enterprise pipeline.

    A pipeline orchestrates multiple workflows.
    """

    def __init__(
        self,
        name: str,
    ) -> None:

        self.pipeline_id = str(
            uuid.uuid4()
        )

        self.name = name

        self.status = PipelineStatus.IDLE

        self.execution_id: str | None = None

        self.created_at = datetime.now(
            timezone.utc
        )

        self.started_at: datetime | None = None

        self.completed_at: datetime | None = None

        self._stages: list[
            PipelineStage
        ] = []

        # ==================================================================
    # Stage Management
    # ==================================================================

    @property
    def stages(self) -> list[PipelineStage]:
        """
        Return all pipeline stages.
        """

        return list(self._stages)

    @property
    def enabled_stages(self) -> list[PipelineStage]:
        """
        Return enabled stages.
        """

        return [
            stage
            for stage in self._stages
            if stage.enabled
        ]

    def add_stage(
        self,
        stage: PipelineStage,
    ) -> None:
        """
        Add a workflow stage.

        Raises
        ------
        ValueError
            If a stage with the same name already exists.
        """

        if self.has_stage(stage.name):

            raise ValueError(
                f"Pipeline stage '{stage.name}' already exists."
            )

        self._stages.append(stage)

        logger.info(
            "Added pipeline stage: %s",
            stage.name,
        )

    def remove_stage(
        self,
        name: str,
    ) -> None:
        """
        Remove a stage.
        """

        stage = self.get_stage(name)

        if stage is None:
            return

        self._stages.remove(stage)

        logger.info(
            "Removed pipeline stage: %s",
            name,
        )

    def get_stage(
        self,
        name: str,
    ) -> PipelineStage | None:
        """
        Return a stage by name.
        """

        for stage in self._stages:

            if stage.name == name:
                return stage

        return None

    def has_stage(
        self,
        name: str,
    ) -> bool:
        """
        Return True if stage exists.
        """

        return self.get_stage(name) is not None

    def enable_stage(
        self,
        name: str,
    ) -> None:
        """
        Enable a stage.
        """

        stage = self.get_stage(name)

        if stage:
            stage.enabled = True

    def disable_stage(
        self,
        name: str,
    ) -> None:
        """
        Disable a stage.
        """

        stage = self.get_stage(name)

        if stage:
            stage.enabled = False

    # ==================================================================
    # Ordering
    # ==================================================================

    def move_stage(
        self,
        name: str,
        new_index: int,
    ) -> None:
        """
        Move a stage.
        """

        stage = self.get_stage(name)

        if stage is None:
            raise KeyError(name)

        self._stages.remove(stage)

        self._stages.insert(
            new_index,
            stage,
        )

    def insert_stage(
        self,
        index: int,
        stage: PipelineStage,
    ) -> None:
        """
        Insert a stage.
        """

        if self.has_stage(stage.name):

            raise ValueError(
                f"Stage '{stage.name}' already exists."
            )

        self._stages.insert(
            index,
            stage,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all stages.
        """

        self._stages.clear()

    # ==================================================================
    # Validation
    # ==================================================================

    def validate(self) -> None:
        """
        Validate the pipeline.
        """

        if not self._stages:

            raise RuntimeError(
                "Pipeline contains no stages."
            )

        names: set[str] = set()

        for stage in self._stages:

            if stage.name in names:

                raise RuntimeError(
                    f"Duplicate stage: {stage.name}"
                )

            names.add(stage.name)

            stage.workflow.validate()

    # ==================================================================
    # Information
    # ==================================================================

    def stage_names(
        self,
    ) -> list[str]:
        """
        Return stage names.
        """

        return [
            stage.name
            for stage in self._stages
        ]

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return pipeline summary.
        """

        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "status": self.status.value,
            "stages": len(self._stages),
            "enabled_stages": len(
                self.enabled_stages
            ),
            "stage_names": self.stage_names(),
        }

    # ==================================================================
    # Utilities
    # ==================================================================

    def __len__(
        self,
    ) -> int:

        return len(self._stages)

    def __iter__(
        self,
    ):

        return iter(self._stages)

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.has_stage(name)

    def __repr__(
        self,
    ) -> str:

        return (
            f"Pipeline("
            f"name={self.name!r}, "
            f"stages={len(self._stages)}, "
            f"status={self.status.value!r})"
        )
        # ==================================================================
    # Execution
    # ==================================================================

    async def run(
        self,
        *,
        director: Any,
        context: Any = None,
    ) -> PipelineResult:
        """
        Execute every enabled workflow in order.

        Parameters
        ----------
        director
            Director instance responsible for executing workflows.

        context
            Shared EngineContext.
        """

        self.validate()

        self.execution_id = str(
            uuid.uuid4()
        )

        self.started_at = datetime.now(
            timezone.utc
        )

        self.status = PipelineStatus.RUNNING

        logger.info(
            "Pipeline started: %s",
            self.name,
        )

        completed: list[str] = []

        failed_workflow: str | None = None

        start = time.perf_counter()

        try:

            for stage in self.enabled_stages:

                logger.info(
                    "Running workflow: %s",
                    stage.name,
                )

                result = await self._run_stage(
                    director=director,
                    stage=stage,
                    context=context,
                )

                if not result.success:

                    failed_workflow = stage.name

                    self.status = (
                        PipelineStatus.FAILED
                    )

                    break

                completed.append(
                    stage.name
                )

            else:

                self.status = (
                    PipelineStatus.COMPLETED
                )

        except Exception:

            logger.exception(
                "Pipeline execution failed."
            )

            self.status = (
                PipelineStatus.FAILED
            )

            raise

        finally:

            self.completed_at = datetime.now(
                timezone.utc
            )

        duration = (
            time.perf_counter()
            - start
        )

        return PipelineResult(
            success=self.status
            == PipelineStatus.COMPLETED,
            pipeline_id=self.pipeline_id,
            execution_id=self.execution_id,
            status=self.status,
            started_at=self.started_at,
            completed_at=self.completed_at,
            duration_seconds=duration,
            completed_workflows=completed,
            failed_workflow=failed_workflow,
        )

    # ==================================================================
    # Execute One Workflow
    # ==================================================================

    async def _run_stage(
        self,
        *,
        director: Any,
        stage: PipelineStage,
        context: Any,
    ):
        """
        Execute a single workflow.
        """

        logger.info(
            "Executing workflow '%s'",
            stage.name,
        )

        return await director.run(
            workflow=stage.workflow,
            context=context,
        )

    # ==================================================================
    # Retry Support
    # ==================================================================

    async def run_stage_with_retry(
        self,
        *,
        director: Any,
        stage: PipelineStage,
        context: Any,
        retries: int = 1,
    ):
        """
        Execute one workflow with retries.
        """

        last_result = None

        for attempt in range(
            retries + 1
        ):

            logger.info(
                "Workflow %s attempt %d",
                stage.name,
                attempt + 1,
            )

            result = await self._run_stage(
                director=director,
                stage=stage,
                context=context,
            )

            last_result = result

            if result.success:
                return result

        return last_result

    # ==================================================================
    # Cancellation
    # ==================================================================

    def cancel(
        self,
    ) -> None:
        """
        Mark the pipeline as cancelled.
        """

        if self.status == PipelineStatus.RUNNING:

            self.status = (
                PipelineStatus.CANCELLED
            )

            logger.warning(
                "Pipeline cancelled."
            )

    # ==================================================================
    # Reset
    # ==================================================================

    def reset(
        self,
    ) -> None:
        """
        Reset runtime state.
        """

        self.status = (
            PipelineStatus.IDLE
        )

        self.execution_id = None

        self.started_at = None

        self.completed_at = None

        # ==================================================================
    # Event Hooks
    # ==================================================================

    async def before_pipeline(
        self,
        context: Any = None,
    ) -> None:
        """
        Hook executed before pipeline execution.

        Override in subclasses.
        """

        logger.info(
            "before_pipeline(): %s",
            self.name,
        )

    async def after_pipeline(
        self,
        result: PipelineResult,
        context: Any = None,
    ) -> None:
        """
        Hook executed after pipeline execution.
        """

        logger.info(
            "after_pipeline(): %s",
            self.name,
        )

    async def before_stage(
        self,
        stage: PipelineStage,
        context: Any = None,
    ) -> None:
        """
        Called before a workflow begins.
        """

        logger.info(
            "before_stage(): %s",
            stage.name,
        )

    async def after_stage(
        self,
        stage: PipelineStage,
        result: Any,
        context: Any = None,
    ) -> None:
        """
        Called after a workflow finishes.
        """

        logger.info(
            "after_stage(): %s",
            stage.name,
        )

    # ==================================================================
    # Metrics
    # ==================================================================

    @property
    def progress(self) -> float:
        """
        Pipeline completion percentage.
        """

        if not self._stages:
            return 0.0

        completed = 0

        for stage in self._stages:

            workflow = stage.workflow

            if hasattr(workflow, "status"):

                status = getattr(
                    workflow,
                    "status",
                    None,
                )

                if str(status).lower().endswith(
                    "completed"
                ):
                    completed += 1

        return (
            completed
            / len(self._stages)
        ) * 100.0

    @property
    def is_finished(
        self,
    ) -> bool:

        return self.status in {
            PipelineStatus.COMPLETED,
            PipelineStatus.FAILED,
            PipelineStatus.CANCELLED,
        }

    @property
    def runtime_seconds(
        self,
    ) -> float:
        """
        Current runtime.
        """

        if self.started_at is None:
            return 0.0

        end = (
            self.completed_at
            or datetime.now(
                timezone.utc
            )
        )

        return (
            end - self.started_at
        ).total_seconds()

    # ==================================================================
    # Execution History
    # ==================================================================

    def execution_summary(
        self,
    ) -> dict[str, Any]:
        """
        Return execution statistics.
        """

        return {
            "pipeline": self.name,
            "pipeline_id": self.pipeline_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "runtime_seconds": self.runtime_seconds,
            "progress": self.progress,
            "stage_count": len(
                self._stages
            ),
            "enabled_stage_count": len(
                self.enabled_stages
            ),
        }

    # ==================================================================
    # Checkpoint
    # ==================================================================

    def checkpoint(
        self,
    ) -> dict[str, Any]:
        """
        Serialize current execution state.

        Can later be written to disk.
        """

        return {

            "pipeline_id": self.pipeline_id,

            "execution_id": self.execution_id,

            "status": self.status.value,

            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),

            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),

            "stages": [

                {
                    "name": stage.name,
                    "enabled": stage.enabled,
                }

                for stage in self._stages
            ],
        }

    # ==================================================================
    # Restore
    # ==================================================================

    def restore_checkpoint(
        self,
        checkpoint: dict[str, Any],
    ) -> None:
        """
        Restore pipeline runtime state.
        """

        self.execution_id = checkpoint.get(
            "execution_id"
        )

        status = checkpoint.get(
            "status"
        )

        if status:

            self.status = PipelineStatus(
                status
            )

    # ==================================================================
    # Logging
    # ==================================================================

    def dump(
        self,
    ) -> None:
        """
        Log pipeline information.
        """

        logger.info(
            "Pipeline: %s",
            self.name,
        )

        logger.info(
            "Status: %s",
            self.status.value,
        )

        logger.info(
            "Stages:"
        )

        for stage in self._stages:

            logger.info(
                "  • %s",
                stage.name,
            )

        # ==================================================================
    # Parallel Execution
    # ==================================================================

    async def run_parallel(
        self,
        *,
        director: "Director",
        context: "EngineContext | None" = None,
    ) -> list[Any]:
        """
        Execute all enabled workflows concurrently.

        Use only when workflows are independent.
        """

        import asyncio

        tasks = []

        for stage in self.enabled_stages:

            tasks.append(

                asyncio.create_task(

                    self._run_stage(
                        director=director,
                        stage=stage,
                        context=context,
                    )
                )
            )

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        return results

    # ==================================================================
    # Serialization
    # ==================================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "pipeline_id": self.pipeline_id,

            "name": self.name,

            "status": self.status.value,

            "stages": [

                {

                    "name": stage.name,

                    "enabled": stage.enabled,

                    "workflow": stage.workflow.summary(),

                    "metadata": stage.metadata,

                }

                for stage in self._stages
            ],
        }

    def to_json(
        self,
        *,
        indent: int = 4,
    ) -> str:

        import json

        return json.dumps(
            self.to_dict(),
            indent=indent,
        )

    # ==================================================================
    # Clone
    # ==================================================================

    def clone(
        self,
    ) -> "Pipeline":

        import copy

        return copy.deepcopy(self)

    # ==================================================================
    # Event Subscribers
    # ==================================================================

    def register_listener(
        self,
        callback,
    ) -> None:

        if not hasattr(
            self,
            "_listeners",
        ):

            self._listeners = []

        self._listeners.append(
            callback
        )

    async def publish_event(
        self,
        event_name: str,
        payload: Any = None,
    ) -> None:

        listeners = getattr(
            self,
            "_listeners",
            [],
        )

        for callback in listeners:

            await callback(
                event_name,
                payload,
            )

    # ==================================================================
    # Health
    # ==================================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return {

            "healthy": True,

            "pipeline": self.name,

            "status": self.status.value,

            "workflow_count": len(
                self._stages
            ),

            "enabled_workflows": len(
                self.enabled_stages
            ),
        }

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:

        return {

            "total_workflows": len(
                self._stages
            ),

            "enabled_workflows": len(
                self.enabled_stages
            ),

            "disabled_workflows":

                len(self._stages)
                - len(self.enabled_stages),

            "runtime_seconds":
                self.runtime_seconds,

            "progress":
                self.progress,

            "status":
                self.status.value,
        }

    # ==================================================================
    # Diagnostics
    # ==================================================================

    def diagnostics(
        self,
    ) -> dict[str, Any]:

        return {

            "summary":
                self.summary(),

            "statistics":
                self.statistics(),

            "checkpoint":
                self.checkpoint(),

            "health":
                self.health(),
        }