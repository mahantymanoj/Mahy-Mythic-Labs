"""
src/agents/master_director.py

Master orchestration agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Coordinate the Studio OS production pipeline
- Manage AgentContext
- Execute specialized agents in the correct order
- Pass outputs between agents
- Track stage results
- Stop the workflow when critical stages fail
- Support selective stage execution
- Support dry-run execution
- Prepare the final publishing package

The MasterDirector does NOT perform the actual work of:
- Research
- Script generation
- Storyboarding
- Image generation
- Video generation
- Narration
- Quality review
- SEO generation
- Publishing

Those responsibilities belong to specialized agents.

Publishing is preparation-only unless a separate explicit
publishing integration is introduced.

Python
------
>= 3.11
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from .base_agent import (
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
    BaseAgent,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# Pipeline Stages
# ==============================================================================


class MasterDirector(BaseAgent):
    """
    Central orchestration agent for Mahy Mythic Labs Studio OS.

    Default pipeline:

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
        Publishing Preparation

    The individual agents are injected into the MasterDirector.
    This keeps the director independent of provider implementations.
    """

    DEFAULT_STAGES = (
        "research",
        "script",
        "storyboard",
        "image",
        "video",
        "narration",
        "quality",
        "seo",
        "publishing",
    )

    CRITICAL_STAGES = {
        "research",
        "script",
        "storyboard",
        "quality",
    }

    def __init__(
        self,
        *,
        agents: dict[str, BaseAgent] | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.MASTER_DIRECTOR,
            name="master_director",
            config=config,
        )

        self.agents: dict[str, BaseAgent] = agents or {}

        self.pipeline_id: str | None = None

        self.pipeline_started_at: datetime | None = None

        self.pipeline_completed_at: datetime | None = None

    # ==========================================================================
    # Initialization
    # ==========================================================================

    async def initialize(
        self,
        context: AgentContext | None = None,
    ) -> bool:
        """
        Initialize the MasterDirector and registered agents.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        for stage, agent in self.agents.items():
            try:
                await agent.initialize(
                    context=self.context
                )

                logger.debug(
                    "Initialized pipeline agent: %s",
                    stage,
                )

            except Exception:
                logger.exception(
                    "Failed to initialize pipeline agent: %s",
                    stage,
                )

                return False

        logger.info(
            "MasterDirector initialized with %d agents.",
            len(self.agents),
        )

        return True

    # ==========================================================================
    # Close
    # ==========================================================================

    async def close(self) -> None:
        """
        Close all registered agents.
        """

        for stage, agent in self.agents.items():
            try:
                await agent.close()

            except Exception:
                logger.exception(
                    "Failed to close agent: %s",
                    stage,
                )

        await super().close()

    # ==========================================================================
    # Agent Registration
    # ==========================================================================

    def register_agent(
        self,
        stage: str,
        agent: BaseAgent,
    ) -> None:
        """
        Register an agent for a pipeline stage.
        """

        normalized_stage = self._normalize_stage(
            stage
        )

        if not isinstance(
            agent,
            BaseAgent,
        ):
            raise TypeError(
                "agent must be an instance of BaseAgent."
            )

        self.agents[
            normalized_stage
        ] = agent

        logger.debug(
            "Registered agent '%s' for stage '%s'.",
            agent.name,
            normalized_stage,
        )

    def unregister_agent(
        self,
        stage: str,
    ) -> BaseAgent | None:
        """
        Remove and return a registered agent.
        """

        normalized_stage = self._normalize_stage(
            stage
        )

        return self.agents.pop(
            normalized_stage,
            None,
        )

    def get_agent(
        self,
        stage: str,
    ) -> BaseAgent | None:
        """
        Retrieve an agent for a pipeline stage.
        """

        normalized_stage = self._normalize_stage(
            stage
        )

        return self.agents.get(
            normalized_stage
        )

    # ==========================================================================
    # Main Execution
    # ==========================================================================

    async def execute(
        self,
        *,
        context: AgentContext | None = None,
        stages: list[str] | tuple[str, ...] | None = None,
        start_from: str | None = None,
        stop_after: str | None = None,
        continue_on_error: bool = False,
        dry_run: bool = False,
        stage_kwargs: dict[str, dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute the Studio OS production pipeline.

        Parameters
        ----------
        context:
            Existing AgentContext.

        stages:
            Explicit list of stages to execute.

            If omitted, DEFAULT_STAGES is used.

        start_from:
            Start from a particular stage.

        stop_after:
            Stop after a particular stage.

        continue_on_error:
            Continue after non-critical stage failure.

        dry_run:
            Validate pipeline configuration without executing
            the agents.

        stage_kwargs:
            Additional keyword arguments for individual stages.

        kwargs:
            Global context values.

        Returns
        -------
        dict[str, Any]
            Complete pipeline execution report.
        """

        if context is not None:
            self.context = context

        if self.context is None:
            self.context = AgentContext()

        # Add global inputs to context.
        for key, value in kwargs.items():
            self.set_context_value(
                key,
                value,
            )

        selected_stages = self._build_stage_list(
            stages=stages,
            start_from=start_from,
            stop_after=stop_after,
        )

        self._validate_pipeline(
            selected_stages
        )

        self.pipeline_id = str(
            uuid.uuid4()
        )

        self.pipeline_started_at = datetime.now(
            timezone.utc
        )

        started_perf = time.perf_counter()

        self.status = AgentStatus.RUNNING

        self.log_info(
            "Starting production pipeline: %s",
            self.pipeline_id,
        )

        pipeline_results: dict[str, Any] = {}

        successful_stages: list[str] = []

        failed_stages: list[str] = []

        skipped_stages: list[str] = []

        if dry_run:
            pipeline_results = self._build_dry_run_results(
                selected_stages
            )

            self.pipeline_completed_at = datetime.now(
                timezone.utc
            )

            self.status = AgentStatus.COMPLETED

            return self._build_pipeline_report(
                pipeline_results=pipeline_results,
                successful_stages=[],
                failed_stages=[],
                skipped_stages=selected_stages,
                duration_seconds=(
                    time.perf_counter()
                    - started_perf
                ),
                dry_run=True,
            )

        # ----------------------------------------------------------------------
        # Execute stages
        # ----------------------------------------------------------------------

        for stage in selected_stages:
            agent = self.agents.get(
                stage
            )

            if agent is None:
                message = (
                    f"No agent registered for stage '{stage}'."
                )

                logger.error(
                    message
                )

                failed_stages.append(
                    stage
                )

                pipeline_results[
                    stage
                ] = {
                    "success": False,
                    "status": "missing_agent",
                    "error": message,
                }

                if (
                    stage in self.CRITICAL_STAGES
                    or not continue_on_error
                ):
                    break

                continue

            self.log_info(
                "Executing stage: %s",
                stage,
            )

            stage_start = time.perf_counter()

            try:
                result = await self._execute_stage(
                    stage=stage,
                    agent=agent,
                    stage_kwargs=(
                        stage_kwargs or {}
                    ).get(
                        stage,
                        {},
                    ),
                )

                pipeline_results[
                    stage
                ] = self._serialize_agent_result(
                    result
                )

                duration = (
                    time.perf_counter()
                    - stage_start
                )

                if result.success:
                    successful_stages.append(
                        stage
                    )

                    self._store_stage_output(
                        stage=stage,
                        result=result,
                    )

                    self.log_info(
                        "Stage completed: %s duration=%.2fs",
                        stage,
                        duration,
                    )

                else:
                    failed_stages.append(
                        stage
                    )

                    self.log_error(
                        "Stage failed: %s error=%s",
                        stage,
                        result.error,
                    )

                    if (
                        stage in self.CRITICAL_STAGES
                        or not continue_on_error
                    ):
                        break

            except Exception as exc:
                failed_stages.append(
                    stage
                )

                pipeline_results[
                    stage
                ] = {
                    "success": False,
                    "status": "exception",
                    "error": str(exc),
                }

                logger.exception(
                    "Unhandled exception in stage: %s",
                    stage,
                )

                if (
                    stage in self.CRITICAL_STAGES
                    or not continue_on_error
                ):
                    break

        # ----------------------------------------------------------------------
        # Determine final status
        # ----------------------------------------------------------------------

        self.pipeline_completed_at = datetime.now(
            timezone.utc
        )

        duration = (
            time.perf_counter()
            - started_perf
        )

        if failed_stages:
            self.status = AgentStatus.FAILED
        else:
            self.status = AgentStatus.COMPLETED

        skipped_stages = [
            stage
            for stage in selected_stages
            if stage not in successful_stages
            and stage not in failed_stages
        ]

        report = self._build_pipeline_report(
            pipeline_results=pipeline_results,
            successful_stages=successful_stages,
            failed_stages=failed_stages,
            skipped_stages=skipped_stages,
            duration_seconds=duration,
            dry_run=False,
        )

        self.set_context_value(
            "pipeline_report",
            report,
        )

        self.set_context_value(
            "pipeline_id",
            self.pipeline_id,
        )

        self.set_metadata(
            "pipeline_status",
            report["status"],
        )

        self.set_metadata(
            "pipeline_duration_seconds",
            duration,
        )

        self.log_info(
            "Production pipeline completed: status=%s duration=%.2fs",
            report["status"],
            duration,
        )

        return report

    # ==========================================================================
    # Stage Execution
    # ==========================================================================

    async def _execute_stage(
        self,
        *,
        stage: str,
        agent: BaseAgent,
        stage_kwargs: dict[str, Any],
    ) -> AgentResult:
        """
        Execute one registered agent.
        """

        if not isinstance(
            stage_kwargs,
            dict,
        ):
            raise TypeError(
                f"stage_kwargs for '{stage}' must be a dictionary."
            )

        result = await agent.run(
            context=self.context,
            **stage_kwargs,
        )

        return result

    # ==========================================================================
    # Store Stage Output
    # ==========================================================================

    def _store_stage_output(
        self,
        *,
        stage: str,
        result: AgentResult,
    ) -> None:
        """
        Store standardized stage output in AgentContext.

        Example:

            script -> context.data["script_output"]
            seo    -> context.data["seo_output"]
        """

        self.set_context_value(
            f"{stage}_output",
            result.output,
        )

        self.set_context_value(
            f"{stage}_result",
            result,
        )

        self.set_context_value(
            "last_completed_stage",
            stage,
        )

    # ==========================================================================
    # Pipeline Construction
    # ==========================================================================

    def _build_stage_list(
        self,
        *,
        stages: list[str] | tuple[str, ...] | None,
        start_from: str | None,
        stop_after: str | None,
    ) -> list[str]:
        """
        Build the final ordered stage list.
        """

        if stages is None:
            selected = list(
                self.DEFAULT_STAGES
            )
        else:
            selected = [
                self._normalize_stage(
                    stage
                )
                for stage in stages
            ]

        if not selected:
            raise ValueError(
                "At least one pipeline stage must be selected."
            )

        # ----------------------------------------------------------------------
        # Start from
        # ----------------------------------------------------------------------

        if start_from is not None:
            normalized_start = self._normalize_stage(
                start_from
            )

            if normalized_start not in selected:
                raise ValueError(
                    f"start_from stage '{normalized_start}' "
                    "is not present in selected stages."
                )

            start_index = selected.index(
                normalized_start
            )

            selected = selected[
                start_index:
            ]

        # ----------------------------------------------------------------------
        # Stop after
        # ----------------------------------------------------------------------

        if stop_after is not None:
            normalized_stop = self._normalize_stage(
                stop_after
            )

            if normalized_stop not in selected:
                raise ValueError(
                    f"stop_after stage '{normalized_stop}' "
                    "is not present in selected stages."
                )

            stop_index = selected.index(
                normalized_stop
            )

            selected = selected[
                : stop_index + 1
            ]

        return selected

    # ==========================================================================
    # Pipeline Validation
    # ==========================================================================

    def _validate_pipeline(
        self,
        stages: list[str],
    ) -> None:
        """
        Validate selected pipeline stages.
        """

        if not stages:
            raise ValueError(
                "Pipeline cannot be empty."
            )

        if len(stages) != len(
            set(stages)
        ):
            raise ValueError(
                "Pipeline contains duplicate stages."
            )

        for stage in stages:
            if stage not in self.DEFAULT_STAGES:
                raise ValueError(
                    f"Unknown pipeline stage: {stage}"
                )

    # ==========================================================================
    # Dry Run
    # ==========================================================================

    def _build_dry_run_results(
        self,
        stages: list[str],
    ) -> dict[str, Any]:
        """
        Build a dry-run report without executing agents.
        """

        results: dict[str, Any] = {}

        for index, stage in enumerate(
            stages,
            start=1,
        ):
            agent = self.agents.get(
                stage
            )

            results[
                stage
            ] = {
                "order": index,
                "agent": (
                    agent.name
                    if agent is not None
                    else None
                ),
                "registered": agent is not None,
                "dry_run": True,
            }

        return results

    # ==========================================================================
    # Pipeline Report
    # ==========================================================================

    def _build_pipeline_report(
        self,
        *,
        pipeline_results: dict[str, Any],
        successful_stages: list[str],
        failed_stages: list[str],
        skipped_stages: list[str],
        duration_seconds: float,
        dry_run: bool,
    ) -> dict[str, Any]:
        """
        Build final pipeline execution report.
        """

        if dry_run:
            status = "dry_run"

        elif failed_stages:
            status = "failed"

        else:
            status = "completed"

        return {
            "pipeline_id": self.pipeline_id,
            "status": status,
            "dry_run": dry_run,
            "started_at": self.pipeline_started_at,
            "completed_at": self.pipeline_completed_at,
            "duration_seconds": round(
                duration_seconds,
                3,
            ),
            "successful_stages": successful_stages,
            "failed_stages": failed_stages,
            "skipped_stages": skipped_stages,
            "stage_results": pipeline_results,
            "publish_ready": self.get_context_value(
                "publish_ready",
                False,
            ),
        }

    # ==========================================================================
    # Serialization
    # ==========================================================================

    @staticmethod
    def _serialize_agent_result(
        result: AgentResult,
    ) -> dict[str, Any]:
        """
        Convert AgentResult into a serializable dictionary.
        """

        return {
            "success": result.success,
            "agent": result.agent.value,
            "output": result.output,
            "execution_id": result.execution_id,
            "status": result.status.value,
            "error": result.error,
            "metadata": result.metadata,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "duration_seconds": result.duration_seconds,
        }

    # ==========================================================================
    # Stage Normalization
    # ==========================================================================

    @staticmethod
    def _normalize_stage(
        stage: str,
    ) -> str:
        """
        Normalize pipeline stage names.
        """

        if not isinstance(
            stage,
            str,
        ):
            raise TypeError(
                "stage must be a string."
            )

        normalized = stage.strip().lower()

        aliases = {
            "research": "research",
            "script": "script",
            "story": "script",
            "storyboard": "storyboard",
            "image": "image",
            "images": "image",
            "video": "video",
            "videos": "video",
            "narration": "narration",
            "audio": "narration",
            "quality": "quality",
            "qa": "quality",
            "seo": "seo",
            "publishing": "publishing",
            "publish": "publishing",
        }

        if normalized not in aliases:
            raise ValueError(
                f"Unknown pipeline stage: {stage!r}"
            )

        return aliases[
            normalized
        ]

    # ==========================================================================
    # Reset
    # ==========================================================================

    def reset_pipeline(
        self,
    ) -> None:
        """
        Reset the MasterDirector pipeline state.
        """

        self.pipeline_id = None

        self.pipeline_started_at = None

        self.pipeline_completed_at = None

        self.reset()

        for agent in self.agents.values():
            agent.reset()

        if self.context is not None:
            self.context.data.pop(
                "pipeline_report",
                None,
            )

            self.context.data.pop(
                "pipeline_id",
                None,
            )

    # ==========================================================================
    # Status
    # ==========================================================================

    def pipeline_status(
        self,
    ) -> dict[str, Any]:
        """
        Return the current pipeline status.
        """

        return {
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "started_at": self.pipeline_started_at,
            "completed_at": self.pipeline_completed_at,
            "registered_agents": {
                stage: agent.name
                for stage, agent in self.agents.items()
            },
        }