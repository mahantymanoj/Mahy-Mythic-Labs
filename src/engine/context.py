"""
src/engine/context.py

Global workflow context for Mahy Mythic Labs Studio OS.

The EngineContext is the single source of truth during a
workflow execution. Every agent, provider and workflow stage
shares information through this object.

Responsibilities
----------------
- Workflow metadata
- Project metadata
- Episode metadata
- Runtime variables
- Agent outputs
- Artifact registry
- Event history
- Metrics
- Configuration
- Serialization support
- Checkpoint support (future)

Python
------
>=3.11
"""

from __future__ import annotations

import copy
import json
import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


# ==============================================================================
# Context Scope
# ==============================================================================


class ContextScope(str, Enum):
    """
    Scope used when storing runtime values.
    """

    GLOBAL = "global"

    WORKFLOW = "workflow"

    PROJECT = "project"

    EPISODE = "episode"

    STAGE = "stage"

    AGENT = "agent"


# ==============================================================================
# Artifact Types
# ==============================================================================


class ArtifactType(str, Enum):
    """
    Files produced during production.
    """

    DOCUMENT = "document"

    SCRIPT = "script"

    STORYBOARD = "storyboard"

    IMAGE = "image"

    VIDEO = "video"

    AUDIO = "audio"

    MUSIC = "music"

    THUMBNAIL = "thumbnail"

    SUBTITLE = "subtitle"

    METADATA = "metadata"

    REPORT = "report"

    JSON = "json"

    OTHER = "other"


# ==============================================================================
# Event Severity
# ==============================================================================


class EventSeverity(str, Enum):
    """
    Event importance.
    """

    DEBUG = "debug"

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"

    CRITICAL = "critical"


# ==============================================================================
# Runtime Metric
# ==============================================================================


@dataclass(slots=True)
class RuntimeMetric:
    """
    Runtime metric.

    Examples
    --------
    execution_time
    token_usage
    api_cost
    memory_usage
    """

    name: str

    value: float | int

    unit: str = ""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Workflow Event
# ==============================================================================


@dataclass(slots=True)
class WorkflowEvent:
    """
    Event generated during workflow execution.
    """

    id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    severity: EventSeverity = (
        EventSeverity.INFO
    )

    source: str = ""

    message: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Artifact
# ==============================================================================


@dataclass(slots=True)
class Artifact:
    """
    Represents a generated production asset.
    """

    id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    name: str = ""

    artifact_type: ArtifactType = (
        ArtifactType.OTHER
    )

    path: str | None = None

    description: str = ""

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    created_by: str = ""

    tags: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Stage Result
# ==============================================================================


@dataclass(slots=True)
class StageResult:
    """
    Standardized workflow stage result.
    """

    stage: str

    success: bool

    output: Any = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Engine Context
# ==============================================================================


class EngineContext:
    """
    Global runtime context shared across the entire Studio OS.

    This class owns:

        - Project information
        - Episode information
        - Workflow state
        - Agent outputs
        - Artifacts
        - Runtime variables
        - Metrics
        - Events

    Every component should exchange information through
    EngineContext instead of directly communicating with each
    other.
    """

    def __init__(
        self,
        *,
        workflow_id: str | None = None,
        project_id: str | None = None,
        episode_id: str | None = None,
    ) -> None:
        """
        Initialize a new EngineContext.
        """

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self.workflow_id = (
            workflow_id
            or str(uuid.uuid4())
        )

        self.project_id = project_id

        self.episode_id = episode_id

        # ------------------------------------------------------------------
        # Timestamps
        # ------------------------------------------------------------------

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at

        # ------------------------------------------------------------------
        # Runtime Variables
        # ------------------------------------------------------------------

        self.variables: dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Agent Outputs
        # ------------------------------------------------------------------

        self.outputs: dict[str, Any] = {}

        # Example:
        #
        # {
        #     "research": {...},
        #     "script": "...",
        #     "seo": {...}
        # }

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        self.metadata: dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self.configuration: dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self.runtime: dict[str, Any] = {
            "status": "created",
            "current_stage": None,
            "last_completed_stage": None,
            "started_at": None,
            "completed_at": None,
        }

        # ------------------------------------------------------------------
        # State Storage
        # ------------------------------------------------------------------

        self.state: dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Events
        # ------------------------------------------------------------------

        self.events: list[WorkflowEvent] = []

        # ------------------------------------------------------------------
        # Metrics
        # ------------------------------------------------------------------

        self.metrics: list[RuntimeMetric] = []

        # ------------------------------------------------------------------
        # Artifacts
        # ------------------------------------------------------------------

        self.artifacts: dict[str, Artifact] = {}

        # ------------------------------------------------------------------
        # Stage Results
        # ------------------------------------------------------------------

        self.stage_results: dict[
            str,
            StageResult,
        ] = {}

    # ======================================================================
    # Internal Helpers
    # ======================================================================

    def _touch(self) -> None:
        """
        Update the last modified timestamp.
        """

        self.updated_at = datetime.now(
            timezone.utc
        )

    # ======================================================================
    # Runtime Variables
    # ======================================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a runtime variable.
        """

        self.variables[key] = value

        self._touch()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a runtime variable.
        """

        return self.variables.get(
            key,
            default,
        )

    def has(
        self,
        key: str,
    ) -> bool:
        """
        Return True if a variable exists.
        """

        return key in self.variables

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a runtime variable.
        """

        self.variables.pop(
            key,
            None,
        )

        self._touch()

    def clear_variables(
        self,
    ) -> None:
        """
        Remove every runtime variable.
        """

        self.variables.clear()

        self._touch()

    # ======================================================================
    # Outputs
    # ======================================================================

    def set_output(
        self,
        stage: str,
        output: Any,
    ) -> None:
        """
        Store output from a workflow stage.
        """

        self.outputs[
            stage
        ] = output

        self.runtime[
            "last_completed_stage"
        ] = stage

        self._touch()

    def get_output(
        self,
        stage: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve stage output.
        """

        return self.outputs.get(
            stage,
            default,
        )

    def has_output(
        self,
        stage: str,
    ) -> bool:
        """
        Return True if stage output exists.
        """

        return stage in self.outputs

    def remove_output(
        self,
        stage: str,
    ) -> None:
        """
        Remove a stage output.
        """

        self.outputs.pop(
            stage,
            None,
        )

        self._touch()

    def clear_outputs(
        self,
    ) -> None:
        """
        Remove every stage output.
        """

        self.outputs.clear()

        self._touch()

    # ======================================================================
    # Metadata
    # ======================================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store metadata.
        """

        self.metadata[key] = value

        self._touch()

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve metadata.
        """

        return self.metadata.get(
            key,
            default,
        )

    def has_metadata(
        self,
        key: str,
    ) -> bool:
        """
        Return True if metadata exists.
        """

        return key in self.metadata

    def remove_metadata(
        self,
        key: str,
    ) -> None:
        """
        Remove metadata.
        """

        self.metadata.pop(
            key,
            None,
        )

        self._touch()

    # ======================================================================
    # Configuration
    # ======================================================================

    def set_config(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store configuration.
        """

        self.configuration[
            key
        ] = value

        self._touch()

    def get_config(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve configuration.
        """

        return self.configuration.get(
            key,
            default,
        )

    def has_config(
        self,
        key: str,
    ) -> bool:
        """
        Return True if configuration exists.
        """

        return key in self.configuration

        # ======================================================================
    # Artifacts
    # ======================================================================

    def add_artifact(
        self,
        artifact: Artifact,
    ) -> None:
        """
        Register a generated artifact.
        """

        self.artifacts[artifact.id] = artifact

        self._touch()

    def create_artifact(
        self,
        *,
        name: str,
        artifact_type: ArtifactType,
        path: str | Path | None = None,
        description: str = "",
        created_by: str = "",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """
        Create and register a new artifact.
        """

        artifact = Artifact(
            name=name,
            artifact_type=artifact_type,
            path=str(path) if path else None,
            description=description,
            created_by=created_by,
            tags=tags or [],
            metadata=metadata or {},
        )

        self.add_artifact(artifact)

        return artifact

    def get_artifact(
        self,
        artifact_id: str,
    ) -> Artifact | None:
        """
        Retrieve an artifact by ID.
        """

        return self.artifacts.get(
            artifact_id
        )

    def find_artifacts(
        self,
        artifact_type: ArtifactType,
    ) -> list[Artifact]:
        """
        Return all artifacts of a given type.
        """

        return [
            artifact
            for artifact in self.artifacts.values()
            if artifact.artifact_type == artifact_type
        ]

    def remove_artifact(
        self,
        artifact_id: str,
    ) -> None:
        """
        Remove an artifact.
        """

        self.artifacts.pop(
            artifact_id,
            None,
        )

        self._touch()

    # ======================================================================
    # Runtime Metrics
    # ======================================================================

    def add_metric(
        self,
        name: str,
        value: float | int,
        *,
        unit: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> RuntimeMetric:
        """
        Record a runtime metric.
        """

        metric = RuntimeMetric(
            name=name,
            value=value,
            unit=unit,
            metadata=metadata or {},
        )

        self.metrics.append(metric)

        self._touch()

        return metric

    def metrics_by_name(
        self,
        name: str,
    ) -> list[RuntimeMetric]:
        """
        Return all metrics matching a name.
        """

        return [
            metric
            for metric in self.metrics
            if metric.name == name
        ]

    def latest_metric(
        self,
        name: str,
    ) -> RuntimeMetric | None:
        """
        Return the most recent metric.
        """

        matches = self.metrics_by_name(name)

        if not matches:
            return None

        return matches[-1]

    def clear_metrics(
        self,
    ) -> None:
        """
        Remove all runtime metrics.
        """

        self.metrics.clear()

        self._touch()

    # ======================================================================
    # Workflow Events
    # ======================================================================

    def add_event(
        self,
        *,
        source: str,
        message: str,
        severity: EventSeverity = EventSeverity.INFO,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowEvent:
        """
        Record a workflow event.
        """

        event = WorkflowEvent(
            source=source,
            message=message,
            severity=severity,
            metadata=metadata or {},
        )

        self.events.append(event)

        self._touch()

        return event

    def get_events(
        self,
        severity: EventSeverity | None = None,
    ) -> list[WorkflowEvent]:
        """
        Retrieve workflow events.
        """

        if severity is None:
            return list(self.events)

        return [
            event
            for event in self.events
            if event.severity == severity
        ]

    def clear_events(
        self,
    ) -> None:
        """
        Remove all workflow events.
        """

        self.events.clear()

        self._touch()

    # ======================================================================
    # Stage Results
    # ======================================================================

    def set_stage_result(
        self,
        result: StageResult,
    ) -> None:
        """
        Store a workflow stage result.
        """

        self.stage_results[
            result.stage
        ] = result

        self.runtime[
            "last_completed_stage"
        ] = result.stage

        self._touch()

    def get_stage_result(
        self,
        stage: str,
    ) -> StageResult | None:
        """
        Retrieve a stage result.
        """

        return self.stage_results.get(
            stage
        )

    def stage_completed(
        self,
        stage: str,
    ) -> bool:
        """
        Return True if a stage completed successfully.
        """

        result = self.get_stage_result(stage)

        return (
            result is not None
            and result.success
        )

    # ======================================================================
    # Runtime Status
    # ======================================================================

    def start_workflow(self) -> None:
        """
        Mark workflow execution as started.
        """

        self.runtime["status"] = "running"

        self.runtime["started_at"] = (
            datetime.now(timezone.utc)
        )

        self._touch()

    def complete_workflow(self) -> None:
        """
        Mark workflow execution as completed.
        """

        self.runtime["status"] = "completed"

        self.runtime["completed_at"] = (
            datetime.now(timezone.utc)
        )

        self._touch()

    def fail_workflow(
        self,
        reason: str,
    ) -> None:
        """
        Mark workflow execution as failed.
        """

        self.runtime["status"] = "failed"

        self.runtime["failure_reason"] = reason

        self.runtime["completed_at"] = (
            datetime.now(timezone.utc)
        )

        self._touch()

    def current_stage(self) -> str | None:
        """
        Return the currently executing stage.
        """

        return self.runtime.get(
            "current_stage"
        )

    def set_current_stage(
        self,
        stage: str | None,
    ) -> None:
        """
        Update the current stage.
        """

        self.runtime[
            "current_stage"
        ] = stage

        self._touch()
        # ======================================================================
    # Serialization
    # ======================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the entire EngineContext into a serializable dictionary.
        """

        return {
            "workflow_id": self.workflow_id,
            "project_id": self.project_id,
            "episode_id": self.episode_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "variables": copy.deepcopy(self.variables),
            "outputs": copy.deepcopy(self.outputs),
            "metadata": copy.deepcopy(self.metadata),
            "configuration": copy.deepcopy(self.configuration),
            "runtime": copy.deepcopy(self.runtime),
            "state": copy.deepcopy(self.state),
            "artifacts": [
                {
                    "id": artifact.id,
                    "name": artifact.name,
                    "artifact_type": artifact.artifact_type.value,
                    "path": artifact.path,
                    "description": artifact.description,
                    "created_at": artifact.created_at.isoformat(),
                    "created_by": artifact.created_by,
                    "tags": artifact.tags,
                    "metadata": artifact.metadata,
                }
                for artifact in self.artifacts.values()
            ],
            "metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "metadata": metric.metadata,
                }
                for metric in self.metrics
            ],
            "events": [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "severity": event.severity.value,
                    "source": event.source,
                    "message": event.message,
                    "metadata": event.metadata,
                }
                for event in self.events
            ],
            "stage_results": {
                stage: {
                    "stage": result.stage,
                    "success": result.success,
                    "output": result.output,
                    "started_at": (
                        result.started_at.isoformat()
                        if result.started_at
                        else None
                    ),
                    "completed_at": (
                        result.completed_at.isoformat()
                        if result.completed_at
                        else None
                    ),
                    "duration_seconds": result.duration_seconds,
                    "metadata": result.metadata,
                }
                for stage, result in self.stage_results.items()
            },
        }

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize the EngineContext to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            default=str,
            ensure_ascii=False,
        )

    # ======================================================================
    # Persistence
    # ======================================================================

    def save(
        self,
        path: str | Path,
    ) -> Path:
        """
        Save the EngineContext as JSON.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.to_json(),
            encoding="utf-8",
        )

        return path

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> "EngineContext":
        """
        Load an EngineContext from a JSON file.
        """

        path = Path(path)

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return cls.from_dict(data)

    # ======================================================================
    # Deserialization
    # ======================================================================

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "EngineContext":
        """
        Reconstruct an EngineContext from a dictionary.
        """

        context = cls(
            workflow_id=data.get("workflow_id"),
            project_id=data.get("project_id"),
            episode_id=data.get("episode_id"),
        )

        context.variables = data.get(
            "variables",
            {},
        )

        context.outputs = data.get(
            "outputs",
            {},
        )

        context.metadata = data.get(
            "metadata",
            {},
        )

        context.configuration = data.get(
            "configuration",
            {},
        )

        context.runtime = data.get(
            "runtime",
            {},
        )

        context.state = data.get(
            "state",
            {},
        )

        # ------------------------------------------------------------------
        # Restore Artifacts
        # ------------------------------------------------------------------

        for item in data.get(
            "artifacts",
            [],
        ):
            artifact = Artifact(
                id=item["id"],
                name=item["name"],
                artifact_type=ArtifactType(
                    item["artifact_type"]
                ),
                path=item.get("path"),
                description=item.get(
                    "description",
                    "",
                ),
                created_at=datetime.fromisoformat(
                    item["created_at"]
                ),
                created_by=item.get(
                    "created_by",
                    "",
                ),
                tags=item.get(
                    "tags",
                    [],
                ),
                metadata=item.get(
                    "metadata",
                    {},
                ),
            )

            context.artifacts[
                artifact.id
            ] = artifact

        # ------------------------------------------------------------------
        # Restore Metrics
        # ------------------------------------------------------------------

        for item in data.get(
            "metrics",
            [],
        ):
            context.metrics.append(
                RuntimeMetric(
                    name=item["name"],
                    value=item["value"],
                    unit=item.get(
                        "unit",
                        "",
                    ),
                    timestamp=datetime.fromisoformat(
                        item["timestamp"]
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
            )

        # ------------------------------------------------------------------
        # Restore Events
        # ------------------------------------------------------------------

        for item in data.get(
            "events",
            [],
        ):
            context.events.append(
                WorkflowEvent(
                    id=item["id"],
                    timestamp=datetime.fromisoformat(
                        item["timestamp"]
                    ),
                    severity=EventSeverity(
                        item["severity"]
                    ),
                    source=item["source"],
                    message=item["message"],
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
            )

        # ------------------------------------------------------------------
        # Restore Stage Results
        # ------------------------------------------------------------------

        for stage, item in data.get(
            "stage_results",
            {},
        ).items():

            context.stage_results[
                stage
            ] = StageResult(
                stage=item["stage"],
                success=item["success"],
                output=item.get("output"),
                started_at=(
                    datetime.fromisoformat(
                        item["started_at"]
                    )
                    if item.get("started_at")
                    else None
                ),
                completed_at=(
                    datetime.fromisoformat(
                        item["completed_at"]
                    )
                    if item.get("completed_at")
                    else None
                ),
                duration_seconds=item.get(
                    "duration_seconds",
                    0.0,
                ),
                metadata=item.get(
                    "metadata",
                    {},
                ),
            )

        return context

        # ======================================================================
    # Snapshot / Clone
    # ======================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Create a complete snapshot of the current context.
        """

        return copy.deepcopy(self.to_dict())

    def clone(self) -> "EngineContext":
        """
        Create a deep copy of this EngineContext.
        """

        return EngineContext.from_dict(
            self.snapshot()
        )

    # ======================================================================
    # Merge
    # ======================================================================

    def merge(
        self,
        other: "EngineContext",
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Merge another EngineContext into this one.
        """

        # Variables
        for key, value in other.variables.items():
            if overwrite or key not in self.variables:
                self.variables[key] = copy.deepcopy(value)

        # Outputs
        for key, value in other.outputs.items():
            if overwrite or key not in self.outputs:
                self.outputs[key] = copy.deepcopy(value)

        # Metadata
        for key, value in other.metadata.items():
            if overwrite or key not in self.metadata:
                self.metadata[key] = copy.deepcopy(value)

        # Configuration
        for key, value in other.configuration.items():
            if overwrite or key not in self.configuration:
                self.configuration[key] = copy.deepcopy(value)

        # Runtime State
        if overwrite:
            self.runtime.update(
                copy.deepcopy(other.runtime)
            )

        # Custom State
        for key, value in other.state.items():
            if overwrite or key not in self.state:
                self.state[key] = copy.deepcopy(value)

        # Artifacts
        for artifact in other.artifacts.values():
            self.artifacts[artifact.id] = copy.deepcopy(
                artifact
            )

        # Events
        self.events.extend(
            copy.deepcopy(other.events)
        )

        # Metrics
        self.metrics.extend(
            copy.deepcopy(other.metrics)
        )

        # Stage Results
        for stage, result in other.stage_results.items():
            if overwrite or stage not in self.stage_results:
                self.stage_results[stage] = copy.deepcopy(
                    result
                )

        self._touch()

    # ======================================================================
    # Reset
    # ======================================================================

    def clear(self) -> None:
        """
        Reset the runtime while keeping workflow identity.
        """

        self.variables.clear()
        self.outputs.clear()
        self.metadata.clear()
        self.configuration.clear()
        self.state.clear()

        self.events.clear()
        self.metrics.clear()
        self.artifacts.clear()
        self.stage_results.clear()

        self.runtime = {
            "status": "created",
            "current_stage": None,
            "last_completed_stage": None,
            "started_at": None,
            "completed_at": None,
        }

        self._touch()

    # ======================================================================
    # Statistics
    # ======================================================================

    @property
    def artifact_count(self) -> int:
        return len(self.artifacts)

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def metric_count(self) -> int:
        return len(self.metrics)

    @property
    def output_count(self) -> int:
        return len(self.outputs)

    @property
    def variable_count(self) -> int:
        return len(self.variables)

    @property
    def completed_stage_count(self) -> int:
        return sum(
            1
            for result in self.stage_results.values()
            if result.success
        )

    # ======================================================================
    # Dictionary Interface
    # ======================================================================

    def __contains__(
        self,
        key: str,
    ) -> bool:
        return key in self.variables

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        return self.variables[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.set(key, value)

    def __delitem__(
        self,
        key: str,
    ) -> None:
        self.remove(key)

    def __len__(self) -> int:
        return len(self.variables)

    def keys(self):
        return self.variables.keys()

    def values(self):
        return self.variables.values()

    def items(self):
        return self.variables.items()

    # ======================================================================
    # Utility
    # ======================================================================

    def update_timestamp(self) -> None:
        """
        Force update of the modification timestamp.
        """

        self._touch()

    def summary(self) -> dict[str, Any]:
        """
        Return a lightweight summary of the current context.
        """

        return {
            "workflow_id": self.workflow_id,
            "project_id": self.project_id,
            "episode_id": self.episode_id,
            "status": self.runtime.get("status"),
            "current_stage": self.runtime.get(
                "current_stage"
            ),
            "variables": self.variable_count,
            "outputs": self.output_count,
            "artifacts": self.artifact_count,
            "events": self.event_count,
            "metrics": self.metric_count,
            "completed_stages": self.completed_stage_count,
        }

    # ======================================================================
    # Representation
    # ======================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"workflow_id={self.workflow_id!r}, "
            f"status={self.runtime.get('status')!r}, "
            f"variables={self.variable_count}, "
            f"outputs={self.output_count}, "
            f"artifacts={self.artifact_count}, "
            f"events={self.event_count})"
        )

    