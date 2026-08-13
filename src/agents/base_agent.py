"""
src/agents/base_agent.py

Universal agent contract for Mahy Mythic Labs Studio OS.

All specialized agents inherit from BaseAgent.

Examples
--------
- ResearchAgent
- ScriptAgent
- StoryboardAgent
- ImageAgent
- VideoAgent
- NarrationAgent
- QualityAgent
- SEOAgent
- PublishingAgent
- MasterDirector

Python
------
>= 3.11
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


# ==============================================================================
# Agent Types
# ==============================================================================


class AgentType(str, Enum):
    """Supported Studio OS agent types."""

    RESEARCH = "research"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    IMAGE = "image"
    VIDEO = "video"
    NARRATION = "narration"
    QUALITY = "quality"
    SEO = "seo"
    PUBLISHING = "publishing"
    MASTER_DIRECTOR = "master_director"


# ==============================================================================
# Agent Status
# ==============================================================================


class AgentStatus(str, Enum):
    """Lifecycle status of an agent execution."""

    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==============================================================================
# Agent Events
# ==============================================================================


class AgentEventType(str, Enum):
    """Events emitted during agent lifecycle."""

    INITIALIZED = "initialized"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CLOSED = "closed"


@dataclass
class AgentEvent:
    """
    Event emitted by an agent during its lifecycle.
    """

    event_type: AgentEventType

    agent: AgentType

    execution_id: str | None = None

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    data: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Agent Result
# ==============================================================================


@dataclass
class AgentResult:
    """
    Standardized result returned by an agent.
    """

    success: bool

    agent: AgentType

    output: Any = None

    execution_id: str = ""

    status: AgentStatus = AgentStatus.COMPLETED

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0


# ==============================================================================
# Agent Context
# ==============================================================================


@dataclass
class AgentContext:
    """
    Runtime context shared with an agent.

    The context provides a common place for agents to access:

    - Project information
    - Episode information
    - Configuration
    - Workflow state
    - Previous agent outputs
    - Runtime metadata
    """

    project_id: str | None = None

    episode_id: str | None = None

    workflow_id: str | None = None

    data: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Event Handler Type
# ==============================================================================


AgentEventHandler = Callable[
    [AgentEvent],
    Awaitable[None],
]


# ==============================================================================
# Base Agent
# ==============================================================================


class BaseAgent(ABC):
    """
    Universal base class for all Studio OS agents.

    Responsibilities
    ----------------
    - Agent identification
    - Lifecycle management
    - Execution tracking
    - Context handling
    - Standardized results
    - Error handling
    - Logging
    - Event emission
    """

    def __init__(
        self,
        agent_type: AgentType,
        *,
        name: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.agent_type = agent_type

        self.name = (
            name
            or agent_type.value
        )

        self.config = config or {}

        self.status = AgentStatus.IDLE

        self.context: AgentContext | None = None

        self.execution_id: str | None = None

        self._started_at: datetime | None = None

        self._completed_at: datetime | None = None

        self._event_handlers: list[
            AgentEventHandler
        ] = []

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def is_running(self) -> bool:
        """
        Return True when the agent is currently executing.
        """

        return self.status == AgentStatus.RUNNING

    @property
    def started_at(self) -> datetime | None:
        """
        Return execution start timestamp.
        """

        return self._started_at

    @property
    def completed_at(self) -> datetime | None:
        """
        Return execution completion timestamp.
        """

        return self._completed_at

    # ==========================================================================
    # Lifecycle
    # ==========================================================================

    async def initialize(
        self,
        context: AgentContext | None = None,
    ) -> bool:
        """
        Initialize the agent.

        Subclasses can override this method when they need
        additional initialization.
        """

        self.status = AgentStatus.INITIALIZING

        if context is not None:
            self.context = context

        self.status = AgentStatus.IDLE

        logger.debug(
            "Initialized agent: %s",
            self.name,
        )

        await self.emit_event(
            AgentEventType.INITIALIZED
        )

        return True

    async def close(self) -> None:
        """
        Release agent resources.

        Subclasses can override this method.
        """

        logger.debug(
            "Closing agent: %s",
            self.name,
        )

        await self.emit_event(
            AgentEventType.CLOSED
        )

        self.status = AgentStatus.IDLE

    # ==========================================================================
    # Event Handling
    # ==========================================================================

    def add_event_handler(
        self,
        handler: AgentEventHandler,
    ) -> None:
        """
        Register an asynchronous event handler.
        """

        if handler not in self._event_handlers:
            self._event_handlers.append(
                handler
            )

    def remove_event_handler(
        self,
        handler: AgentEventHandler,
    ) -> None:
        """
        Remove a previously registered event handler.
        """

        if handler in self._event_handlers:
            self._event_handlers.remove(
                handler
            )

    async def emit_event(
        self,
        event_type: AgentEventType,
        *,
        data: dict[str, Any] | None = None,
    ) -> None:
        """
        Emit an agent lifecycle event.

        Event-handler failures are isolated from agent execution.
        """

        event = AgentEvent(
            event_type=event_type,
            agent=self.agent_type,
            execution_id=self.execution_id,
            data=data or {},
        )

        for handler in tuple(
            self._event_handlers
        ):
            try:
                await handler(event)

            except Exception:
                logger.exception(
                    "Agent event handler failed. "
                    "agent=%s event=%s",
                    self.name,
                    event_type.value,
                )

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def run(
        self,
        *,
        context: AgentContext | None = None,
        **kwargs: Any,
    ) -> AgentResult:
        """
        Execute the agent.

        This is the common entry point used by the workflow engine.

        Subclasses implement their actual work in `execute()`.
        """

        if context is not None:
            self.context = context

        self.execution_id = str(
            uuid.uuid4()
        )

        self._started_at = datetime.now(
            timezone.utc
        )

        self._completed_at = None

        start_time = time.perf_counter()

        self.status = AgentStatus.RUNNING

        logger.info(
            "Agent started: %s execution_id=%s",
            self.name,
            self.execution_id,
        )

        await self.emit_event(
            AgentEventType.STARTED
        )

        try:
            output = await self.execute(
                **kwargs
            )

            self.status = AgentStatus.COMPLETED

            self._completed_at = datetime.now(
                timezone.utc
            )

            duration = (
                time.perf_counter()
                - start_time
            )

            logger.info(
                "Agent completed: %s "
                "execution_id=%s duration=%.2fs",
                self.name,
                self.execution_id,
                duration,
            )

            await self.emit_event(
                AgentEventType.COMPLETED,
                data={
                    "duration_seconds": duration,
                },
            )

            return AgentResult(
                success=True,
                agent=self.agent_type,
                output=output,
                execution_id=self.execution_id,
                status=self.status,
                started_at=self._started_at,
                completed_at=self._completed_at,
                duration_seconds=duration,
            )

        except asyncio.CancelledError:
            self.status = AgentStatus.CANCELLED

            self._completed_at = datetime.now(
                timezone.utc
            )

            duration = (
                time.perf_counter()
                - start_time
            )

            logger.warning(
                "Agent cancelled: %s "
                "execution_id=%s",
                self.name,
                self.execution_id,
            )

            await self.emit_event(
                AgentEventType.CANCELLED,
                data={
                    "duration_seconds": duration,
                },
            )

            raise

        except Exception as exc:
            self.status = AgentStatus.FAILED

            self._completed_at = datetime.now(
                timezone.utc
            )

            duration = (
                time.perf_counter()
                - start_time
            )

            logger.exception(
                "Agent failed: %s "
                "execution_id=%s",
                self.name,
                self.execution_id,
            )

            await self.emit_event(
                AgentEventType.FAILED,
                data={
                    "error": str(exc),
                    "duration_seconds": duration,
                },
            )

            return AgentResult(
                success=False,
                agent=self.agent_type,
                output=None,
                execution_id=self.execution_id,
                status=self.status,
                error=str(exc),
                started_at=self._started_at,
                completed_at=self._completed_at,
                duration_seconds=duration,
            )

    # ==========================================================================
    # Abstract Execution
    # ==========================================================================

    @abstractmethod
    async def execute(
        self,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the agent's core responsibility.

        Every concrete agent must implement this method.
        """

        raise NotImplementedError

    # ==========================================================================
    # Context Helpers
    # ==========================================================================

    def set_context(
        self,
        context: AgentContext,
    ) -> None:
        """
        Set the runtime context.
        """

        self.context = context

    def get_context_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a value from the current agent context.
        """

        if self.context is None:
            return default

        return self.context.data.get(
            key,
            default,
        )

    def set_context_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value in the current agent context.
        """

        if self.context is None:
            self.context = AgentContext()

        self.context.data[key] = value

    def require_context(self) -> AgentContext:
        """
        Return the current context.

        Raises
        ------
        RuntimeError
            If the agent has no context.
        """

        if self.context is None:
            raise RuntimeError(
                f"Agent '{self.name}' requires an AgentContext."
            )

        return self.context

    def require_context_value(
        self,
        key: str,
    ) -> Any:
        """
        Retrieve a required value from the current context.

        Raises
        ------
        KeyError
            If the requested value does not exist.
        """

        context = self.require_context()

        if key not in context.data:
            raise KeyError(
                f"Required context value '{key}' "
                f"was not found for agent '{self.name}'."
            )

        return context.data[key]

    # ==========================================================================
    # Metadata Helpers
    # ==========================================================================

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve metadata from the current context.
        """

        if self.context is None:
            return default

        return self.context.metadata.get(
            key,
            default,
        )

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store metadata in the current agent context.
        """

        if self.context is None:
            self.context = AgentContext()

        self.context.metadata[key] = value

    # ==========================================================================
    # Logging Helpers
    # ==========================================================================

    def log_info(
        self,
        message: str,
        *args: Any,
    ) -> None:
        """
        Write an informational agent log message.
        """

        logger.info(
            "[%s] %s",
            self.name,
            message,
            *args,
        )

    def log_warning(
        self,
        message: str,
        *args: Any,
    ) -> None:
        """
        Write a warning agent log message.
        """

        logger.warning(
            "[%s] %s",
            self.name,
            message,
            *args,
        )

    def log_error(
        self,
        message: str,
        *args: Any,
    ) -> None:
        """
        Write an error agent log message.
        """

        logger.error(
            "[%s] %s",
            self.name,
            message,
            *args,
        )

    # ==========================================================================
    # Cancellation
    # ==========================================================================

    def cancel(self) -> None:
        """
        Mark the agent as cancelled.

        This does not forcibly terminate an asyncio task.
        The workflow/task manager is responsible for cancelling
        the actual task.
        """

        if self.status == AgentStatus.RUNNING:
            self.status = AgentStatus.CANCELLED

            logger.warning(
                "Agent marked as cancelled: %s",
                self.name,
            )

    # ==========================================================================
    # Status
    # ==========================================================================

    def reset(
        self,
        *,
        clear_context: bool = False,
    ) -> None:
        """
        Reset the agent to its initial idle state.

        Parameters
        ----------
        clear_context:
            If True, remove the current AgentContext.
        """

        self.status = AgentStatus.IDLE

        self.execution_id = None

        self._started_at = None

        self._completed_at = None

        if clear_context:
            self.context = None

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"agent_type={self.agent_type.value!r}, "
            f"status={self.status.value!r})"
        )