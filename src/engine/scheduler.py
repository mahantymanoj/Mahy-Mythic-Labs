"""
src/engine/scheduler.py

Enterprise Scheduler for Mahy Mythic Labs Studio OS.

Responsible for executing asynchronous tasks using various
scheduling strategies.

Python
------
>=3.11
"""

from __future__ import annotations

import asyncio
import heapq
import logging
import time

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from itertools import count
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

# ==============================================================================
# Scheduler Status
# ==============================================================================


class SchedulerStatus(str, Enum):

    IDLE = "idle"

    RUNNING = "running"

    PAUSED = "paused"

    STOPPED = "stopped"

    CANCELLED = "cancelled"


# ==============================================================================
# Task Priority
# ==============================================================================


class TaskPriority(int, Enum):

    CRITICAL = 0

    HIGH = 1

    NORMAL = 2

    LOW = 3

    BACKGROUND = 4


# ==============================================================================
# Scheduled Task
# ==============================================================================


@dataclass(slots=True)
class ScheduledTask:
    """
    One scheduled task.
    """

    name: str

    coroutine: Callable[..., Awaitable[Any]]

    priority: TaskPriority = TaskPriority.NORMAL

    retries: int = 0

    timeout: float | None = None

    delay: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Task Result
# ==============================================================================


@dataclass(slots=True)
class TaskResult:

    task_name: str

    success: bool

    result: Any = None

    exception: Exception | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0


# ==============================================================================
# Scheduler
# ==============================================================================


class Scheduler:

    """
    Enterprise async scheduler.
    """

    def __init__(
        self,
        *,
        max_concurrent_tasks: int = 5,
    ):

        self.status = SchedulerStatus.IDLE

        self.max_concurrent_tasks = max_concurrent_tasks

        self._counter = count()

        self._queue: list[
            tuple[
                int,
                int,
                ScheduledTask,
            ]
        ] = []

        self._running_tasks: set[
            asyncio.Task
        ] = set()

        self._completed: list[
            TaskResult
        ] = []

        self._semaphore = asyncio.Semaphore(
            max_concurrent_tasks
        )

        # ==================================================================
    # Queue Management
    # ==================================================================

    def schedule(
        self,
        task: ScheduledTask,
    ) -> None:
        """
        Schedule a task.

        Lower priority values execute first.
        """

        heapq.heappush(
            self._queue,
            (
                int(task.priority),
                next(self._counter),
                task,
            ),
        )

        logger.info(
            "Scheduled task: %s",
            task.name,
        )

    def schedule_many(
        self,
        tasks: list[ScheduledTask],
    ) -> None:
        """
        Schedule multiple tasks.
        """

        for task in tasks:
            self.schedule(task)

    # ==================================================================
    # Queue Inspection
    # ==================================================================

    @property
    def queue_size(
        self,
    ) -> int:
        """
        Number of queued tasks.
        """

        return len(self._queue)

    @property
    def running_count(
        self,
    ) -> int:
        """
        Number of active tasks.
        """

        return len(self._running_tasks)

    @property
    def completed_count(
        self,
    ) -> int:
        """
        Number of completed tasks.
        """

        return len(self._completed)

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Return True if queue is empty.
        """

        return len(self._queue) == 0

    def peek(
        self,
    ) -> ScheduledTask | None:
        """
        Return the next task without removing it.
        """

        if not self._queue:
            return None

        return self._queue[0][2]

    # ==================================================================
    # Queue Removal
    # ==================================================================

    def pop(
        self,
    ) -> ScheduledTask | None:
        """
        Remove and return the next task.
        """

        if not self._queue:
            return None

        _, _, task = heapq.heappop(
            self._queue
        )

        return task

    def clear(
        self,
    ) -> None:
        """
        Remove all queued tasks.
        """

        self._queue.clear()

        logger.info(
            "Scheduler queue cleared."
        )

    # ==================================================================
    # Remove Task By Name
    # ==================================================================

    def remove(
        self,
        task_name: str,
    ) -> bool:
        """
        Remove a task by name.

        Returns
        -------
        bool
            True if removed.
        """

        for index, item in enumerate(
            self._queue
        ):

            _, _, task = item

            if task.name == task_name:

                self._queue.pop(index)

                heapq.heapify(
                    self._queue
                )

                logger.info(
                    "Removed task: %s",
                    task_name,
                )

                return True

        return False

    # ==================================================================
    # Lookup
    # ==================================================================

    def has_task(
        self,
        task_name: str,
    ) -> bool:

        return any(
            task.name == task_name
            for _, _, task in self._queue
        )

    def get_task(
        self,
        task_name: str,
    ) -> ScheduledTask | None:

        for _, _, task in self._queue:

            if task.name == task_name:
                return task

        return None

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:

        return {

            "status":
                self.status.value,

            "queued_tasks":
                self.queue_size,

            "running_tasks":
                self.running_count,

            "completed_tasks":
                self.completed_count,

            "max_concurrent":
                self.max_concurrent_tasks,
        }

    # ==================================================================
    # Utilities
    # ==================================================================

    def __len__(
        self,
    ) -> int:

        return len(self._queue)

    def __bool__(
        self,
    ) -> bool:

        return not self.is_empty

    def __repr__(
        self,
    ) -> str:

        return (

            f"Scheduler("

            f"queued={len(self._queue)}, "

            f"running={len(self._running_tasks)}, "

            f"completed={len(self._completed)}, "

            f"status={self.status.value!r})"

        )

        # ==================================================================
    # Execute One Task
    # ==================================================================

    async def _execute_task(
        self,
        task: ScheduledTask,
    ) -> TaskResult:
        """
        Execute a single scheduled task.
        """

        started_at = datetime.now(
            timezone.utc
        )

        start = time.perf_counter()

        async with self._semaphore:

            current = asyncio.current_task()

            if current is not None:
                self._running_tasks.add(
                    current
                )

            try:

                if task.delay > 0:

                    await asyncio.sleep(
                        task.delay
                    )

                logger.info(
                    "Executing task: %s",
                    task.name,
                )

                if task.timeout:

                    result = await asyncio.wait_for(
                        task.coroutine(),
                        timeout=task.timeout,
                    )

                else:

                    result = await task.coroutine()

                duration = (
                    time.perf_counter()
                    - start
                )

                task_result = TaskResult(
                    task_name=task.name,
                    success=True,
                    result=result,
                    started_at=started_at,
                    completed_at=datetime.now(
                        timezone.utc
                    ),
                    duration_seconds=duration,
                )

                self._completed.append(
                    task_result
                )

                return task_result

            except Exception as exc:

                duration = (
                    time.perf_counter()
                    - start
                )

                logger.exception(
                    "Task failed: %s",
                    task.name,
                )

                task_result = TaskResult(
                    task_name=task.name,
                    success=False,
                    exception=exc,
                    started_at=started_at,
                    completed_at=datetime.now(
                        timezone.utc
                    ),
                    duration_seconds=duration,
                )

                self._completed.append(
                    task_result
                )

                return task_result

            finally:

                if current is not None:
                    self._running_tasks.discard(
                        current
                    )

    # ==================================================================
    # Retry Engine
    # ==================================================================

    async def _execute_with_retry(
        self,
        task: ScheduledTask,
    ) -> TaskResult:
        """
        Execute a task with retry support.
        """

        attempts = task.retries + 1

        last_result: TaskResult | None = None

        for attempt in range(
            attempts
        ):

            logger.info(
                "Task '%s' attempt %d/%d",
                task.name,
                attempt + 1,
                attempts,
            )

            result = await self._execute_task(
                task
            )

            if result.success:

                return result

            last_result = result

            if attempt < task.retries:

                await asyncio.sleep(
                    1.0
                )

        assert last_result is not None

        return last_result

    # ==================================================================
    # Sequential Execution
    # ==================================================================

    async def run(
        self,
    ) -> list[TaskResult]:
        """
        Execute tasks sequentially.
        """

        self.status = (
            SchedulerStatus.RUNNING
        )

        results: list[
            TaskResult
        ] = []

        while self._queue:

            task = self.pop()

            if task is None:
                break

            result = (
                await self._execute_with_retry(
                    task
                )
            )

            results.append(
                result
            )

        self.status = (
            SchedulerStatus.IDLE
        )

        return results

    # ==================================================================
    # Parallel Execution
    # ==================================================================

    async def run_parallel(
        self,
    ) -> list[TaskResult]:
        """
        Execute queued tasks concurrently.
        """

        self.status = (
            SchedulerStatus.RUNNING
        )

        tasks: list[
            asyncio.Task
        ] = []

        while self._queue:

            task = self.pop()

            if task is None:
                continue

            tasks.append(

                asyncio.create_task(

                    self._execute_with_retry(
                        task
                    )
                )
            )

        results = await asyncio.gather(
            *tasks,
            return_exceptions=False,
        )

        self.status = (
            SchedulerStatus.IDLE
        )

        return list(results)

    # ==================================================================
    # Convenience
    # ==================================================================

    async def run_task(
        self,
        task: ScheduledTask,
    ) -> TaskResult:
        """
        Execute one task immediately.
        """

        return await self._execute_with_retry(
            task
        )

        # ==================================================================
    # Dependency Graph
    # ==================================================================

    def dependencies_satisfied(
        self,
        task: ScheduledTask,
        completed: set[str],
    ) -> bool:
        """
        Return True if every dependency has completed.
        """

        depends_on = task.metadata.get(
            "depends_on",
            [],
        )

        return all(
            dependency in completed
            for dependency in depends_on
        )

    async def run_dependency_graph(
        self,
    ) -> list[TaskResult]:
        """
        Execute tasks respecting dependency graph.
        """

        self.status = SchedulerStatus.RUNNING

        completed: set[str] = set()

        pending = list(self._queue)

        self._queue.clear()

        results: list[TaskResult] = []

        while pending:

            progress = False

            remaining = []

            for _, _, task in pending:

                if self.dependencies_satisfied(
                    task,
                    completed,
                ):

                    result = await self._execute_with_retry(
                        task
                    )

                    results.append(result)

                    if result.success:

                        completed.add(
                            task.name
                        )

                    progress = True

                else:

                    remaining.append(
                        (
                            int(task.priority),
                            next(self._counter),
                            task,
                        )
                    )

            if not progress:

                raise RuntimeError(
                    "Circular dependency detected."
                )

            pending = remaining

        self.status = SchedulerStatus.IDLE

        return results

    # ==================================================================
    # Pause / Resume
    # ==================================================================

    def pause(
        self,
    ) -> None:

        self.status = SchedulerStatus.PAUSED

        logger.info(
            "Scheduler paused."
        )

    def resume(
        self,
    ) -> None:

        if self.status == SchedulerStatus.PAUSED:

            self.status = SchedulerStatus.RUNNING

            logger.info(
                "Scheduler resumed."
            )

    # ==================================================================
    # Cancel Running Tasks
    # ==================================================================

    async def cancel_all(
        self,
    ) -> None:

        logger.warning(
            "Cancelling %d running tasks.",
            len(self._running_tasks),
        )

        for task in list(
            self._running_tasks
        ):

            task.cancel()

        if self._running_tasks:

            await asyncio.gather(
                *self._running_tasks,
                return_exceptions=True,
            )

        self._running_tasks.clear()

        self.status = SchedulerStatus.CANCELLED

    # ==================================================================
    # Worker Pool
    # ==================================================================

    async def worker(
        self,
        worker_name: str,
    ) -> None:
        """
        Worker loop.
        """

        logger.info(
            "Worker started: %s",
            worker_name,
        )

        while self.status == SchedulerStatus.RUNNING:

            task = self.pop()

            if task is None:

                return

            await self._execute_with_retry(
                task
            )

    async def run_workers(
        self,
        worker_count: int,
    ) -> None:
        """
        Execute tasks using worker pool.
        """

        self.status = SchedulerStatus.RUNNING

        workers = [

            asyncio.create_task(

                self.worker(
                    f"worker-{index+1}"
                )

            )

            for index in range(
                worker_count
            )

        ]

        await asyncio.gather(
            *workers
        )

        self.status = SchedulerStatus.IDLE

    # ==================================================================
    # Backoff
    # ==================================================================

    async def retry_delay(
        self,
        attempt: int,
    ) -> None:
        """
        Exponential retry delay.
        """

        delay = min(
            2 ** attempt,
            30,
        )

        await asyncio.sleep(
            delay
        )

