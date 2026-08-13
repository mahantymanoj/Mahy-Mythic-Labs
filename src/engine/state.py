"""
src/engine/state.py

Enterprise State Manager for Mahy Mythic Labs Studio OS.

Provides a centralized runtime state store with
checkpointing and persistence support.

Python
------
>=3.11
"""

from __future__ import annotations

import copy
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any

logger = logging.getLogger(__name__)


# ==============================================================================
# State Status
# ==============================================================================


class StateStatus(str, Enum):

    INITIALIZED = "initialized"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"


# ==============================================================================
# State Snapshot
# ==============================================================================


@dataclass(slots=True)
class StateSnapshot:
    """
    Immutable checkpoint.
    """

    version: int

    timestamp: datetime

    state: dict[str, Any]

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# State Manager
# ==============================================================================


class StateManager:
    """
    Enterprise runtime state manager.
    """

    def __init__(
        self,
    ) -> None:

        self._lock = RLock()

        self._state: dict[
            str,
            Any,
        ] = {}

        self._version = 1

        self.status = StateStatus.INITIALIZED

        self._history: list[
            StateSnapshot
        ] = []

        logger.info(
            "StateManager initialized."
        )
        # ==================================================================
    # Basic CRUD Operations
    # ==================================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value.

        Supports nested keys:

            engine.status
            workflow.current
            agents.image.output
        """

        with self._lock:

            parts = key.split(".")

            current = self._state

            for part in parts[:-1]:

                current = current.setdefault(
                    part,
                    {}
                )

            current[
                parts[-1]
            ] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a value.
        """

        with self._lock:

            current = self._state

            for part in key.split("."):

                if (
                    not isinstance(
                        current,
                        dict,
                    )
                    or part not in current
                ):
                    return default

                current = current[part]

            return current

    def delete(
        self,
        key: str,
    ) -> bool:
        """
        Delete a value.

        Returns True if removed.
        """

        with self._lock:

            parts = key.split(".")

            current = self._state

            for part in parts[:-1]:

                if part not in current:
                    return False

                current = current[part]

            return (
                current.pop(
                    parts[-1],
                    None,
                )
                is not None
            )

    # ==================================================================
    # Existence
    # ==================================================================

    def exists(
        self,
        key: str,
    ) -> bool:

        sentinel = object()

        return (
            self.get(
                key,
                sentinel,
            )
            is not sentinel
        )

    # ==================================================================
    # Bulk Operations
    # ==================================================================

    def update(
        self,
        values: dict[str, Any],
    ) -> None:
        """
        Bulk update.

        Keys may use dot notation.
        """

        with self._lock:

            for key, value in values.items():

                self.set(
                    key,
                    value,
                )

    def clear(
        self,
    ) -> None:
        """
        Remove all runtime state.
        """

        with self._lock:

            self._state.clear()

    # ==================================================================
    # State Access
    # ==================================================================

    def as_dict(
        self,
    ) -> dict[str, Any]:
        """
        Return a deep copy of state.
        """

        with self._lock:

            return copy.deepcopy(
                self._state
            )

    # ==================================================================
    # Merge
    # ==================================================================

    def merge(
        self,
        other: dict[str, Any],
    ) -> None:
        """
        Merge another dictionary.
        """

        def recursive_merge(
            target: dict[str, Any],
            source: dict[str, Any],
        ) -> None:

            for key, value in source.items():

                if (

                    key in target

                    and isinstance(
                        target[key],
                        dict,
                    )

                    and isinstance(
                        value,
                        dict,
                    )

                ):

                    recursive_merge(
                        target[key],
                        value,
                    )

                else:

                    target[key] = copy.deepcopy(
                        value
                    )

        with self._lock:

            recursive_merge(
                self._state,
                other,
            )

    # ==================================================================
    # Atomic Update
    # ==================================================================

    def atomic_update(
        self,
        key: str,
        updater,
    ) -> Any:
        """
        Atomically update a value.

        Example

            state.atomic_update(
                "counter",
                lambda value: (value or 0) + 1
            )
        """

        with self._lock:

            current = self.get(key)

            new_value = updater(
                current
            )

            self.set(
                key,
                new_value,
            )

            return new_value

    # ==================================================================
    # Dictionary Interface
    # ==================================================================

    def __getitem__(
        self,
        key: str,
    ) -> Any:

        value = self.get(key)

        if value is None:

            raise KeyError(key)

        return value

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.set(
            key,
            value,
        )

    def __contains__(
        self,
        key: str,
    ) -> bool:

        return self.exists(key)

    def __len__(
        self,
    ) -> int:

        return len(
            self._state
        )

    def __repr__(
        self,
    ) -> str:

        return (

            f"StateManager("

            f"version={self._version}, "

            f"status={self.status.value!r}, "

            f"keys={len(self._state)})"

        )
        # ==================================================================
    # Version Management
    # ==================================================================

    @property
    def version(
        self,
    ) -> int:
        """
        Current state version.
        """
        return self._version

    def increment_version(
        self,
    ) -> int:
        """
        Increment the internal version.
        """

        with self._lock:

            self._version += 1

            return self._version

    # ==================================================================
    # Snapshot
    # ==================================================================

    def snapshot(
        self,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> StateSnapshot:
        """
        Create an immutable checkpoint.
        """

        with self._lock:

            snapshot = StateSnapshot(

                version=self._version,

                timestamp=datetime.now(
                    timezone.utc,
                ),

                state=copy.deepcopy(
                    self._state,
                ),

                metadata=metadata or {},
            )

            self._history.append(
                snapshot,
            )

            return snapshot

    # ==================================================================
    # History
    # ==================================================================

    @property
    def history(
        self,
    ) -> list[StateSnapshot]:
        """
        Return snapshot history.
        """

        return list(
            self._history,
        )

    def latest_snapshot(
        self,
    ) -> StateSnapshot | None:
        """
        Return newest snapshot.
        """

        if not self._history:
            return None

        return self._history[-1]

    # ==================================================================
    # Restore
    # ==================================================================

    def restore(
        self,
        snapshot: StateSnapshot,
    ) -> None:
        """
        Restore a previous snapshot.
        """

        with self._lock:

            self._state = copy.deepcopy(
                snapshot.state,
            )

            self._version = snapshot.version

            logger.info(
                "Restored snapshot version %d",
                snapshot.version,
            )

    # ==================================================================
    # Rollback
    # ==================================================================

    def rollback(
        self,
    ) -> bool:
        """
        Roll back to the previous snapshot.

        Returns
        -------
        bool
            True if successful.
        """

        with self._lock:

            if len(self._history) < 2:
                return False

            #
            # Remove current snapshot
            #

            self._history.pop()

            previous = self._history[-1]

            self.restore(
                previous,
            )

            return True

    # ==================================================================
    # Transactions
    # ==================================================================

    def begin_transaction(
        self,
    ) -> StateSnapshot:
        """
        Begin a transaction.

        A transaction is simply a snapshot
        that can later be restored.
        """

        logger.debug(
            "Transaction started."
        )

        return self.snapshot()

    def commit(
        self,
    ) -> None:
        """
        Commit transaction.

        Simply increments version.
        """

        self.increment_version()

        logger.debug(
            "Transaction committed."
        )

    def rollback_transaction(
        self,
        snapshot: StateSnapshot,
    ) -> None:
        """
        Roll back to the transaction snapshot.
        """

        logger.warning(
            "Transaction rolled back."
        )

        self.restore(
            snapshot,
        )

    # ==================================================================
    # Snapshot Cleanup
    # ==================================================================

    def clear_history(
        self,
    ) -> None:
        """
        Remove all stored snapshots.
        """

        with self._lock:

            self._history.clear()

    def trim_history(
        self,
        keep_last: int,
    ) -> None:
        """
        Keep only the most recent snapshots.
        """

        with self._lock:

            if keep_last <= 0:

                self._history.clear()

            else:

                self._history = (
                    self._history[
                        -keep_last:
                    ]
                )

        # ==================================================================
    # Persistence
    # ==================================================================

    def save(
        self,
        file_path: str | Path,
    ) -> None:
        """
        Save the current state to a JSON file.
        """

        path = Path(file_path)

        with self._lock:

            payload = {

                "version": self._version,

                "status": self.status.value,

                "saved_at": datetime.now(
                    timezone.utc
                ).isoformat(),

                "state": self._state,
            }

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                json.dumps(
                    payload,
                    indent=4,
                    default=str,
                ),
                encoding="utf-8",
            )

        logger.info(
            "State saved to %s",
            path,
        )

    # ==================================================================
    # Load
    # ==================================================================

    def load(
        self,
        file_path: str | Path,
    ) -> None:
        """
        Load state from a JSON file.
        """

        path = Path(file_path)

        if not path.exists():

            raise FileNotFoundError(path)

        payload = json.loads(

            path.read_text(
                encoding="utf-8",
            )
        )

        with self._lock:

            self._version = payload.get(
                "version",
                1,
            )

            status = payload.get(
                "status",
                StateStatus.INITIALIZED.value,
            )

            self.status = StateStatus(
                status
            )

            self._state = payload.get(
                "state",
                {},
            )

        logger.info(
            "State loaded from %s",
            path,
        )

    # ==================================================================
    # Auto Save
    # ==================================================================

    def autosave(
        self,
        directory: str | Path,
    ) -> Path:
        """
        Save a timestamped checkpoint.
        """

        directory = Path(directory)

        filename = (

            datetime.now(
                timezone.utc
            )

            .strftime(
                "%Y%m%d_%H%M%S"
            )

            + ".json"
        )

        checkpoint = (
            directory / filename
        )

        self.save(
            checkpoint
        )

        return checkpoint

    # ==================================================================
    # Recovery
    # ==================================================================

    def recover_latest(
        self,
        directory: str | Path,
    ) -> Path | None:
        """
        Recover the latest checkpoint.
        """

        directory = Path(directory)

        if not directory.exists():

            return None

        files = sorted(

            directory.glob(
                "*.json"
            )

        )

        if not files:

            return None

        latest = files[-1]

        self.load(
            latest
        )

        logger.info(
            "Recovered checkpoint %s",
            latest,
        )

        return latest

    # ==================================================================
    # Export / Import
    # ==================================================================

    def export(
        self,
    ) -> dict[str, Any]:
        """
        Export current state.
        """

        with self._lock:

            return {

                "version":
                    self._version,

                "status":
                    self.status.value,

                "state":
                    copy.deepcopy(
                        self._state
                    ),
            }

    def import_state(
        self,
        payload: dict[str, Any],
    ) -> None:
        """
        Import state from a dictionary.
        """

        with self._lock:

            self._version = payload.get(
                "version",
                1,
            )

            self.status = StateStatus(

                payload.get(
                    "status",
                    StateStatus.INITIALIZED.value,
                )

            )

            self._state = copy.deepcopy(

                payload.get(
                    "state",
                    {},
                )

            )

    # ==================================================================
    # Checkpoints
    # ==================================================================

    def create_checkpoint(
        self,
        directory: str | Path,
        *,
        name: str | None = None,
    ) -> Path:
        """
        Create a named checkpoint.
        """

        directory = Path(directory)

        if name is None:

            name = (

                "checkpoint_"

                + datetime.now(
                    timezone.utc
                ).strftime(
                    "%Y%m%d_%H%M%S"
                )

            )

        checkpoint = (
            directory / f"{name}.json"
        )

        self.save(
            checkpoint
        )

        return checkpoint

        # ==================================================================
    # Observer Management
    # ==================================================================

    def __init__(self) -> None:
        ...
        self._observers: list[
            callable
        ] = []

    def add_observer(
        self,
        observer,
    ) -> None:
        """
        Register a state observer.

        Observer signature:

            observer(
                key,
                old_value,
                new_value
            )
        """

        self._observers.append(
            observer
        )

    def remove_observer(
        self,
        observer,
    ) -> None:

        if observer in self._observers:

            self._observers.remove(
                observer
            )

    def _notify(
        self,
        key: str,
        old_value: Any,
        new_value: Any,
    ) -> None:

        for observer in self._observers:

            try:

                observer(
                    key,
                    old_value,
                    new_value,
                )

            except Exception:

                logger.exception(
                    "State observer failed."
                )

    # ==================================================================
    # Change Tracking
    # ==================================================================

    def update_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Update a value and notify observers.
        """

        old = self.get(key)

        self.set(
            key,
            value,
        )

        self.increment_version()

        self._notify(
            key,
            old,
            value,
        )

    # ==================================================================
    # Diff
    # ==================================================================

    def diff(
        self,
        snapshot: StateSnapshot,
    ) -> dict[str, Any]:
        """
        Compute differences between the current
        state and a snapshot.
        """

        current = self.as_dict()

        changes = {}

        keys = (

            set(current)

            | set(snapshot.state)

        )

        for key in keys:

            if current.get(key) != snapshot.state.get(key):

                changes[key] = {

                    "old":
                        snapshot.state.get(key),

                    "new":
                        current.get(key),
                }

        return changes

    # ==================================================================
    # Diagnostics
    # ==================================================================

    def diagnostics(
        self,
    ) -> dict[str, Any]:

        return {

            "version":
                self.version,

            "status":
                self.status.value,

            "history":
                len(self._history),

            "keys":
                len(self._state),

            "observers":
                len(self._observers),
        }

    # ==================================================================
    # Health
    # ==================================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return {

            "healthy": True,

            "status":
                self.status.value,

            "version":
                self.version,

            "history_size":
                len(self._history),
        }

    # ==================================================================
    # Metrics
    # ==================================================================

    def metrics(
        self,
    ) -> dict[str, Any]:

        return {

            "keys":
                len(self._state),

            "snapshots":
                len(self._history),

            "version":
                self.version,

            "observer_count":
                len(self._observers),
        }

    # ==================================================================
    # Lifecycle
    # ==================================================================

    def start(
        self,
    ) -> None:

        self.status = (
            StateStatus.RUNNING
        )

    def pause(
        self,
    ) -> None:

        self.status = (
            StateStatus.PAUSED
        )

    def complete(
        self,
    ) -> None:

        self.status = (
            StateStatus.COMPLETED
        )

    def fail(
        self,
    ) -> None:

        self.status = (
            StateStatus.FAILED
        )

    # ==================================================================
    # Representation
    # ==================================================================

    def __str__(
        self,
    ) -> str:

        return (

            f"StateManager("

            f"status={self.status.value}, "

            f"version={self.version}, "

            f"keys={len(self._state)}, "

            f"snapshots={len(self._history)})"

        )