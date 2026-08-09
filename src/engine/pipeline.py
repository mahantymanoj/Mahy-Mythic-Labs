"""DAG Pipeline Engine for Mahy Mythic Labs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, List, Dict

from src.enums import WorkflowStatus
from src.engine.context import PipelineContext
from src.engine.state import StateManager

logger = logging.getLogger("mahy.engine.pipeline")


class PipelineStage:
    """Base class for a pipeline stage task."""

    def __init__(self, name: str) -> None:
        self.name = name

    def execute(self, ctx: PipelineContext) -> bool:
        raise NotImplementedError


class Pipeline:
    """DAG Pipeline Execution Runner with state checkpoints."""

    def __init__(self, context: PipelineContext) -> None:
        self.ctx = context
        self.stages: List[PipelineStage] = []

    def add_stage(self, stage: PipelineStage) -> Pipeline:
        self.stages.append(stage)
        return self

    def run(self) -> bool:
        """Run all pipeline stages, skipping completed stages."""
        logger.info(f"Starting pipeline for episode {self.ctx.config.episode_id}")
        self.ctx.state.status = WorkflowStatus.RUNNING
        StateManager.save(self.ctx.state_file, self.ctx.state)

        for stage in self.stages:
            if stage.name in self.ctx.state.completed_stages:
                logger.info(f"Skipping already completed stage: {stage.name}")
                continue

            logger.info(f"Executing stage: {stage.name}")
            self.ctx.state.current_stage = stage.name
            StateManager.save(self.ctx.state_file, self.ctx.state)

            try:
                success = stage.execute(self.ctx)
                if not success:
                    logger.error(f"Stage failed: {stage.name}")
                    self.ctx.state.status = WorkflowStatus.FAILED
                    self.ctx.state.errors.append(f"Stage failed: {stage.name}")
                    StateManager.save(self.ctx.state_file, self.ctx.state)
                    return False

                self.ctx.state.completed_stages.append(stage.name)
                StateManager.save(self.ctx.state_file, self.ctx.state)
            except Exception as err:
                logger.exception(f"Exception in stage {stage.name}: {err}")
                self.ctx.state.status = WorkflowStatus.FAILED
                self.ctx.state.errors.append(str(err))
                StateManager.save(self.ctx.state_file, self.ctx.state)
                return False

        self.ctx.state.status = WorkflowStatus.SUCCESS
        self.ctx.state.current_stage = "completed"
        StateManager.save(self.ctx.state_file, self.ctx.state)
        logger.info("Pipeline completed successfully!")
        return True
