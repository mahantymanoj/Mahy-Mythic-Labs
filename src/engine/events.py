"""
src/engine/events.py

Enterprise Event Bus for Mahy Mythic Labs Studio OS.

All workflow components communicate through events instead of
calling each other directly.

Example
-------
ResearchAgent
        │
        ▼
Publish(RESEARCH_COMPLETED)
        │
        ▼
EventBus
        │
 ┌──────┼───────────┐
 ▼      ▼           ▼
ScriptAgent
Logger
MasterDirector

Python
------
>=3.11
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import traceback
import uuid

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ==============================================================================
# Event Priority
# ==============================================================================


class EventPriority(int, Enum):
    """
    Event execution priority.
    """

    LOW = 10

    NORMAL = 20

    HIGH = 30

    CRITICAL = 40


# ==============================================================================
# Event Type
# ==============================================================================


class EventType(str, Enum):
    """
    Standard Studio OS events.
    """

    # Workflow
    WORKFLOW_STARTED = "workflow.started"

    WORKFLOW_COMPLETED = "workflow.completed"

    WORKFLOW_FAILED = "workflow.failed"

    WORKFLOW_CANCELLED = "workflow.cancelled"

    # Agent

    AGENT_INITIALIZED = "agent.initialized"

    AGENT_STARTED = "agent.started"

    AGENT_COMPLETED = "agent.completed"

    AGENT_FAILED = "agent.failed"

    AGENT_CANCELLED = "agent.cancelled"

    # Research

    RESEARCH_STARTED = "research.started"

    RESEARCH_COMPLETED = "research.completed"

    # Script

    SCRIPT_STARTED = "script.started"

    SCRIPT_COMPLETED = "script.completed"

    # Storyboard

    STORYBOARD_STARTED = "storyboard.started"

    STORYBOARD_COMPLETED = "storyboard.completed"

    # Image

    IMAGE_STARTED = "image.started"

    IMAGE_GENERATED = "image.generated"

    IMAGE_FAILED = "image.failed"

    # Video

    VIDEO_STARTED = "video.started"

    VIDEO_GENERATED = "video.generated"

    VIDEO_FAILED = "video.failed"

    # Narration

    NARRATION_STARTED = "narration.started"

    NARRATION_COMPLETED = "narration.completed"

    # SEO

    SEO_STARTED = "seo.started"

    SEO_COMPLETED = "seo.completed"

    # Publishing

    PUBLISH_STARTED = "publish.started"

    PUBLISH_COMPLETED = "publish.completed"

    # Generic

    ERROR = "system.error"

    WARNING = "system.warning"

    INFO = "system.info"

    DEBUG = "system.debug"


# ==============================================================================
# Event
# ==============================================================================


@dataclass(slots=True)
class Event:
    """
    Standard event object.
    """

    event_type: EventType

    source: str

    payload: dict[str, Any] = field(
        default_factory=dict
    )

    priority: EventPriority = EventPriority.NORMAL

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    correlation_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Event Subscription
# ==============================================================================


@dataclass(slots=True)
class Subscription:
    """
    Registered event listener.
    """

    event_type: str

    callback: Any

    once: bool = False

    enabled: bool = True

    priority: EventPriority = EventPriority.NORMAL

# ==============================================================================
# Event Bus
# ==============================================================================


class EventBus:
    """
    Enterprise asynchronous event bus.

    Features
    --------
    - Publish / Subscribe
    - Async + Sync callbacks
    - Wildcard subscriptions
    - One-time listeners
    - Event history
    - Thread-safe publishing
    """

    def __init__(self) -> None:

        # event_name -> subscriptions
        self._subscriptions: dict[
            str,
            list[Subscription],
        ] = defaultdict(list)

        # previously published events
        self._history: list[Event] = []

        # protect concurrent publish()
        self._lock = asyncio.Lock()

    # ======================================================================
    # Subscription
    # ======================================================================

    def subscribe(
        self,
        event_type: EventType | str,
        callback: Any,
        *,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> Subscription:
        """
        Subscribe to an event.

        Example
        -------
        bus.subscribe(
            EventType.AGENT_COMPLETED,
            my_handler,
        )
        """

        key = (
            event_type.value
            if isinstance(event_type, EventType)
            else event_type
        )

        subscription = Subscription(
            event_type=key,
            callback=callback,
            priority=priority,
        )

        self._subscriptions[key].append(
            subscription
        )

        self._subscriptions[key].sort(
            key=lambda s: s.priority,
            reverse=True,
        )

        logger.debug(
            "Subscribed %s -> %s",
            callback,
            key,
        )

        return subscription

    def subscribe_once(
        self,
        event_type: EventType | str,
        callback: Any,
        *,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> Subscription:
        """
        Subscribe once.

        Listener is automatically removed after
        first invocation.
        """

        key = (
            event_type.value
            if isinstance(event_type, EventType)
            else event_type
        )

        subscription = Subscription(
            event_type=key,
            callback=callback,
            once=True,
            priority=priority,
        )

        self._subscriptions[key].append(
            subscription
        )

        self._subscriptions[key].sort(
            key=lambda s: s.priority,
            reverse=True,
        )

        return subscription

    # ======================================================================
    # Unsubscribe
    # ======================================================================

    def unsubscribe(
        self,
        subscription: Subscription,
    ) -> bool:
        """
        Remove an existing subscription.
        """

        listeners = self._subscriptions.get(
            subscription.event_type
        )

        if not listeners:
            return False

        try:
            listeners.remove(subscription)

            return True

        except ValueError:
            return False

    def unsubscribe_callback(
        self,
        event_type: EventType | str,
        callback: Any,
    ) -> int:
        """
        Remove all listeners registered for a callback.

        Returns
        -------
        Number removed.
        """

        key = (
            event_type.value
            if isinstance(event_type, EventType)
            else event_type
        )

        listeners = self._subscriptions.get(
            key,
            [],
        )

        removed = 0

        remaining: list[
            Subscription
        ] = []

        for sub in listeners:

            if sub.callback == callback:
                removed += 1

            else:
                remaining.append(sub)

        self._subscriptions[key] = remaining

        return removed

    # ======================================================================
    # Enable / Disable
    # ======================================================================

    def enable(
        self,
        subscription: Subscription,
    ) -> None:
        """
        Enable a listener.
        """

        subscription.enabled = True

    def disable(
        self,
        subscription: Subscription,
    ) -> None:
        """
        Disable a listener.
        """

        subscription.enabled = False

    # ======================================================================
    # Inspection
    # ======================================================================

    def listeners(
        self,
        event_type: EventType | str,
    ) -> list[Subscription]:
        """
        Return listeners for an event.
        """

        key = (
            event_type.value
            if isinstance(event_type, EventType)
            else event_type
        )

        return list(
            self._subscriptions.get(
                key,
                [],
            )
        )

    def listener_count(
        self,
        event_type: EventType | str,
    ) -> int:
        """
        Number of registered listeners.
        """

        return len(
            self.listeners(event_type)
        )

    def clear(
        self,
    ) -> None:
        """
        Remove every subscription.
        """

        self._subscriptions.clear()

    # ======================================================================
    # Event History
    # ======================================================================

    @property
    def history(
        self,
    ) -> list[Event]:
        """
        Published events.
        """

        return list(self._history)

    def clear_history(
        self,
    ) -> None:
        """
        Remove stored event history.
        """

        self._history.clear()

    # ======================================================================
    # Publishing
    # ======================================================================

    async def publish(
        self,
        event: Event,
    ) -> None:
        """
        Publish an event to all matching subscribers.

        Supports:
        - Exact event listeners
        - Wildcard "*" listeners
        - Sync callbacks
        - Async callbacks
        """

        async with self._lock:

            self._history.append(event)

            listeners: list[Subscription] = []

            # Exact listeners
            listeners.extend(
                self._subscriptions.get(
                    event.event_type.value,
                    [],
                )
            )

            # Wildcard listeners
            listeners.extend(
                self._subscriptions.get(
                    "*",
                    [],
                )
            )

            if not listeners:
                return

            listeners.sort(
                key=lambda s: s.priority,
                reverse=True,
            )

            remove_after_call: list[
                Subscription
            ] = []

            for subscription in listeners:

                if not subscription.enabled:
                    continue

                try:
                    await self._execute_callback(
                        subscription.callback,
                        event,
                    )

                    if subscription.once:
                        remove_after_call.append(
                            subscription
                        )

                except Exception:

                    logger.exception(
                        "Event handler failed "
                        "event=%s callback=%s",
                        event.event_type.value,
                        getattr(
                            subscription.callback,
                            "__name__",
                            repr(subscription.callback),
                        ),
                    )

            for subscription in remove_after_call:
                self.unsubscribe(subscription)

    # ======================================================================
    # Callback Execution
    # ======================================================================

    async def _execute_callback(
        self,
        callback: Any,
        event: Event,
    ) -> None:
        """
        Execute either an async or synchronous callback.
        """

        if inspect.iscoroutinefunction(
            callback,
        ):
            await callback(event)
            return

        result = callback(event)

        if inspect.isawaitable(result):
            await result

    # ======================================================================
    # Convenience Publishing
    # ======================================================================

    async def emit(
        self,
        event_type: EventType,
        *,
        source: str,
        payload: dict[str, Any] | None = None,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Event:
        """
        Convenience wrapper around publish().
        """

        event = Event(
            event_type=event_type,
            source=source,
            payload=payload or {},
            priority=priority,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )

        await self.publish(event)

        return event

    # ======================================================================
    # Queries
    # ======================================================================

    def last_event(
        self,
    ) -> Event | None:
        """
        Return the most recently published event.
        """

        if not self._history:
            return None

        return self._history[-1]

    def events_of_type(
        self,
        event_type: EventType | str,
    ) -> list[Event]:
        """
        Return all events of the specified type.
        """

        key = (
            event_type.value
            if isinstance(event_type, EventType)
            else event_type
        )

        return [
            event
            for event in self._history
            if event.event_type.value == key
        ]

    def find_events(
        self,
        *,
        source: str | None = None,
    ) -> list[Event]:
        """
        Find events by source.
        """

        if source is None:
            return list(self._history)

        return [
            event
            for event in self._history
            if event.source == source
        ]

    # ======================================================================
    # Utility
    # ======================================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return EventBus statistics.
        """

        return {
            "subscriptions": sum(
                len(v)
                for v in self._subscriptions.values()
            ),
            "event_types": len(
                self._subscriptions
            ),
            "published_events": len(
                self._history
            ),
        }

    def __len__(
        self,
    ) -> int:
        """
        Number of published events.
        """

        return len(self._history)

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}("
            f"subscriptions={sum(len(v) for v in self._subscriptions.values())}, "
            f"events={len(self._history)})"
        )


# ==============================================================================
# Global Event Bus
# ==============================================================================

_global_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """
    Return the singleton EventBus instance.
    """

    return _global_event_bus