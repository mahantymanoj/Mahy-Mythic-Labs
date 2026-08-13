"""
src/engine/workflow.py

Workflow definition system for Mahy Mythic Labs Studio OS.

A Workflow describes HOW a production pipeline is organized.
It does not execute the workflow—that responsibility belongs
to the Director.

Features
--------
- Directed workflow graph (DAG)
- Stage dependencies
- Conditional execution
- Retry policies
- Parallel stages
- Validation
- Serialization
- Reusable workflow templates

Python
------
>=3.11
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import copy
import json
import uuid

from src.engine.director import WorkflowStage


# ==============================================================================
# Stage Status
# ==============================================================================


class StageStatus(str, Enum):
    """
    Runtime state of a workflow node.
    """

    PENDING = "pending"

    READY = "ready"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    SKIPPED = "skipped"

    CANCELLED = "cancelled"


# ==============================================================================
# Retry Policy
# ==============================================================================


@dataclass(slots=True)
class RetryPolicy:
    """
    Retry configuration for a workflow stage.
    """

    max_retries: int = 1

    delay_seconds: float = 0.0

    exponential_backoff: bool = False

    max_delay: float = 60.0


# ==============================================================================
# Stage Condition
# ==============================================================================


@dataclass(slots=True)
class StageCondition:
    """
    Conditional execution rule.
    """

    enabled: bool = True

    expression: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Workflow Node
# ==============================================================================


@dataclass(slots=True)
class WorkflowNode:
    """
    One node inside the workflow graph.
    """

    stage: WorkflowStage

    name: str

    description: str = ""

    enabled: bool = True

    parallel: bool = False

    timeout: int | None = None

    retry_policy: RetryPolicy = field(
        default_factory=RetryPolicy
    )

    condition: StageCondition = field(
        default_factory=StageCondition
    )

    depends_on: list[
        WorkflowStage
    ] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Workflow Definition
# ==============================================================================


@dataclass(slots=True)
class WorkflowDefinition:
    """
    Complete workflow definition.
    """

    id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    name: str = "Studio Workflow"

    description: str = ""

    version: str = "1.0"

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    nodes: list[
        WorkflowNode
    ] = field(
        default_factory=list
    )


# ==============================================================================
# Workflow
# ==============================================================================


class Workflow:
    """
    Enterprise workflow definition.

    This class represents the workflow graph only.
    Execution is handled by Director.
    """

    def __init__(
        self,
        definition: WorkflowDefinition | None = None,
    ) -> None:

        self.definition = (
            definition
            or WorkflowDefinition()
        )

        self._node_lookup: dict[
            WorkflowStage,
            WorkflowNode,
        ] = {}

        for node in self.definition.nodes:
            self._node_lookup[
                node.stage
            ] = node

        # ==================================================================
    # Node Registration
    # ==================================================================

    def add_node(
        self,
        node: WorkflowNode,
    ) -> None:
        """
        Add a workflow node.

        Raises
        ------
        ValueError
            If a node for the stage already exists.
        """

        if node.stage in self._node_lookup:
            raise ValueError(
                f"Workflow node already exists for "
                f"stage '{node.stage.value}'."
            )

        self.definition.nodes.append(node)

        self._node_lookup[node.stage] = node

    def remove_node(
        self,
        stage: WorkflowStage,
    ) -> None:
        """
        Remove a workflow node.
        """

        if stage not in self._node_lookup:
            return

        node = self._node_lookup.pop(stage)

        self.definition.nodes.remove(node)

        # Remove dependencies referencing this node
        for other in self.definition.nodes:

            if stage in other.depends_on:
                other.depends_on.remove(stage)

    # ==================================================================
    # Lookup
    # ==================================================================

    def get_node(
        self,
        stage: WorkflowStage,
    ) -> WorkflowNode | None:
        """
        Retrieve a workflow node.
        """

        return self._node_lookup.get(stage)

    def has_node(
        self,
        stage: WorkflowStage,
    ) -> bool:
        """
        Return True if the workflow contains the stage.
        """

        return stage in self._node_lookup

    @property
    def nodes(
        self,
    ) -> list[WorkflowNode]:
        """
        Return all workflow nodes.
        """

        return list(self.definition.nodes)

    @property
    def enabled_nodes(
        self,
    ) -> list[WorkflowNode]:
        """
        Return enabled workflow nodes.
        """

        return [
            node
            for node in self.definition.nodes
            if node.enabled
        ]

    # ==================================================================
    # Dependencies
    # ==================================================================

    def add_dependency(
        self,
        stage: WorkflowStage,
        depends_on: WorkflowStage,
    ) -> None:
        """
        Add a dependency between two stages.

        stage
            Depends on depends_on.
        """

        node = self.get_node(stage)

        if node is None:
            raise KeyError(stage.value)

        if depends_on not in self._node_lookup:
            raise KeyError(depends_on.value)

        if depends_on not in node.depends_on:
            node.depends_on.append(depends_on)

    def remove_dependency(
        self,
        stage: WorkflowStage,
        depends_on: WorkflowStage,
    ) -> None:
        """
        Remove a dependency.
        """

        node = self.get_node(stage)

        if node is None:
            return

        if depends_on in node.depends_on:
            node.depends_on.remove(depends_on)

    def dependencies(
        self,
        stage: WorkflowStage,
    ) -> list[WorkflowStage]:
        """
        Return dependencies for a stage.
        """

        node = self.get_node(stage)

        if node is None:
            return []

        return list(node.depends_on)

    def dependents(
        self,
        stage: WorkflowStage,
    ) -> list[WorkflowStage]:
        """
        Return stages that depend on this stage.
        """

        result: list[WorkflowStage] = []

        for node in self.definition.nodes:

            if stage in node.depends_on:
                result.append(node.stage)

        return result

    # ==================================================================
    # Validation
    # ==================================================================

    def validate(self) -> None:
        """
        Validate workflow consistency.

        Raises
        ------
        ValueError
            If invalid dependencies are detected.
        """

        for node in self.definition.nodes:

            for dependency in node.depends_on:

                if dependency not in self._node_lookup:

                    raise ValueError(
                        f"{node.stage.value} depends on "
                        f"unknown stage "
                        f"'{dependency.value}'."
                    )

                if dependency == node.stage:

                    raise ValueError(
                        f"Stage '{node.stage.value}' "
                        f"cannot depend on itself."
                    )

        self._validate_cycles()

    def _validate_cycles(
        self,
    ) -> None:
        """
        Detect dependency cycles using DFS.
        """

        visited: set[
            WorkflowStage
        ] = set()

        active: set[
            WorkflowStage
        ] = set()

        def dfs(
            stage: WorkflowStage,
        ) -> None:

            if stage in active:

                raise ValueError(
                    "Workflow contains "
                    "circular dependencies."
                )

            if stage in visited:
                return

            visited.add(stage)

            active.add(stage)

            node = self.get_node(stage)

            if node:

                for dependency in node.depends_on:
                    dfs(dependency)

            active.remove(stage)

        for node in self.definition.nodes:
            dfs(node.stage)

    # ==================================================================
    # Factory
    # ==================================================================

    @classmethod
    def default_workflow(
        cls,
    ) -> "Workflow":
        """
        Create the default Studio OS workflow.
        """

        workflow = cls()

        stages = [
            WorkflowStage.RESEARCH,
            WorkflowStage.SCRIPT,
            WorkflowStage.STORYBOARD,
            WorkflowStage.IMAGE,
            WorkflowStage.VIDEO,
            WorkflowStage.NARRATION,
            WorkflowStage.QUALITY,
            WorkflowStage.SEO,
            WorkflowStage.PUBLISHING,
        ]

        previous: WorkflowStage | None = None

        for stage in stages:

            node = WorkflowNode(
                stage=stage,
                name=stage.value.title(),
            )

            workflow.add_node(node)

            if previous is not None:
                workflow.add_dependency(
                    stage,
                    previous,
                )

            previous = stage

        return workflow

        # ==================================================================
    # Topological Sorting
    # ==================================================================

    def execution_order(
        self,
    ) -> list[WorkflowNode]:
        """
        Return the workflow in dependency-safe order.

        Uses Kahn's algorithm for topological sorting.

        Raises
        ------
        RuntimeError
            If a cycle is detected.
        """

        in_degree: dict[
            WorkflowStage,
            int,
        ] = {}

        graph: dict[
            WorkflowStage,
            list[WorkflowStage],
        ] = {}

        # Initialize
        for node in self.enabled_nodes:

            in_degree[node.stage] = len(
                node.depends_on
            )

            graph[node.stage] = []

        # Build reverse graph
        for node in self.enabled_nodes:

            for dependency in node.depends_on:

                if dependency in graph:

                    graph[dependency].append(
                        node.stage
                    )

        ready = [
            stage
            for stage, degree in in_degree.items()
            if degree == 0
        ]

        ordered: list[
            WorkflowNode
        ] = []

        while ready:

            current = ready.pop(0)

            ordered.append(
                self.get_node(current)
            )

            for child in graph[current]:

                in_degree[child] -= 1

                if in_degree[child] == 0:
                    ready.append(child)

        if len(ordered) != len(self.enabled_nodes):

            raise RuntimeError(
                "Unable to determine execution order. "
                "Workflow may contain a cycle."
            )

        return ordered

    # ==================================================================
    # Parallel Groups
    # ==================================================================

    def parallel_groups(
        self,
    ) -> list[list[WorkflowNode]]:
        """
        Group workflow nodes that can execute in parallel.

        Returns
        -------
        Example

        [
            [Research],
            [Script],
            [Storyboard],
            [Image, Narration],
            [Video],
            [Quality],
            ...
        ]
        """

        remaining = {
            node.stage: set(node.depends_on)
            for node in self.enabled_nodes
        }

        groups: list[
            list[WorkflowNode]
        ] = []

        while remaining:

            ready = [

                stage

                for stage, deps in remaining.items()

                if not deps
            ]

            if not ready:

                raise RuntimeError(
                    "Circular dependency detected."
                )

            groups.append(
                [
                    self.get_node(stage)
                    for stage in ready
                ]
            )

            for stage in ready:

                remaining.pop(stage)

            for deps in remaining.values():

                deps.difference_update(ready)

        return groups

    # ==================================================================
    # Ready Nodes
    # ==================================================================

    def ready_nodes(
        self,
        completed: set[WorkflowStage],
    ) -> list[WorkflowNode]:
        """
        Return nodes that are ready to execute.
        """

        ready: list[
            WorkflowNode
        ] = []

        for node in self.enabled_nodes:

            if node.stage in completed:
                continue

            if all(
                dependency in completed
                for dependency in node.depends_on
            ):
                ready.append(node)

        return ready

    # ==================================================================
    # Conditional Execution
    # ==================================================================

    def should_execute(
        self,
        node: WorkflowNode,
        variables: dict[str, Any] | None = None,
    ) -> bool:
        """
        Evaluate whether a workflow node should execute.

        Notes
        -----
        The expression engine is intentionally simple.
        Later versions can integrate CEL or JsonLogic.
        """

        if not node.enabled:
            return False

        if not node.condition.enabled:
            return False

        expression = node.condition.expression

        if not expression:
            return True

        variables = variables or {}

        try:

            return bool(
                eval(
                    expression,
                    {},
                    variables,
                )
            )

        except Exception:

            return False

    # ==================================================================
    # Traversal
    # ==================================================================

    def root_nodes(
        self,
    ) -> list[WorkflowNode]:
        """
        Nodes without dependencies.
        """

        return [

            node

            for node in self.enabled_nodes

            if not node.depends_on
        ]

    def leaf_nodes(
        self,
    ) -> list[WorkflowNode]:
        """
        Nodes that nothing depends upon.
        """

        dependent_nodes = set()

        for node in self.enabled_nodes:

            dependent_nodes.update(
                node.depends_on
            )

        return [

            node

            for node in self.enabled_nodes

            if node.stage not in dependent_nodes
        ]

    def descendants(
        self,
        stage: WorkflowStage,
    ) -> list[WorkflowStage]:
        """
        Return every stage reachable from the given stage.
        """

        visited: set[
            WorkflowStage
        ] = set()

        def dfs(
            current: WorkflowStage,
        ) -> None:

            for child in self.dependents(current):

                if child in visited:
                    continue

                visited.add(child)

                dfs(child)

        dfs(stage)

        return list(visited)

    def ancestors(
        self,
        stage: WorkflowStage,
    ) -> list[WorkflowStage]:
        """
        Return all ancestor stages.
        """

        visited: set[
            WorkflowStage
        ] = set()

        def dfs(
            current: WorkflowStage,
        ) -> None:

            node = self.get_node(current)

            if node is None:
                return

            for dependency in node.depends_on:

                if dependency in visited:
                    continue

                visited.add(dependency)

                dfs(dependency)

        dfs(stage)

        return list(visited)

        # ==================================================================
    # Serialization
    # ==================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the workflow into a dictionary.
        """

        return {
            "id": self.definition.id,
            "name": self.definition.name,
            "description": self.definition.description,
            "version": self.definition.version,
            "created_at": self.definition.created_at.isoformat(),
            "metadata": copy.deepcopy(
                self.definition.metadata
            ),
            "nodes": [
                {
                    "stage": node.stage.value,
                    "name": node.name,
                    "description": node.description,
                    "enabled": node.enabled,
                    "parallel": node.parallel,
                    "timeout": node.timeout,
                    "depends_on": [
                        dependency.value
                        for dependency in node.depends_on
                    ],
                    "retry_policy": {
                        "max_retries": (
                            node.retry_policy.max_retries
                        ),
                        "delay_seconds": (
                            node.retry_policy.delay_seconds
                        ),
                        "exponential_backoff": (
                            node.retry_policy.exponential_backoff
                        ),
                        "max_delay": (
                            node.retry_policy.max_delay
                        ),
                    },
                    "condition": {
                        "enabled": (
                            node.condition.enabled
                        ),
                        "expression": (
                            node.condition.expression
                        ),
                    },
                    "metadata": copy.deepcopy(
                        node.metadata
                    ),
                }
                for node in self.definition.nodes
            ],
        }

    def to_json(
        self,
        *,
        indent: int = 4,
    ) -> str:
        """
        Serialize the workflow as JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
        )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Workflow":
        """
        Build a workflow from a dictionary.
        """

        definition = WorkflowDefinition(
            id=data["id"],
            name=data["name"],
            description=data.get(
                "description",
                "",
            ),
            version=data.get(
                "version",
                "1.0",
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

        workflow = cls(definition)

        for item in data["nodes"]:

            node = WorkflowNode(
                stage=WorkflowStage(
                    item["stage"]
                ),
                name=item["name"],
                description=item.get(
                    "description",
                    "",
                ),
                enabled=item.get(
                    "enabled",
                    True,
                ),
                parallel=item.get(
                    "parallel",
                    False,
                ),
                timeout=item.get(
                    "timeout",
                ),
            )

            retry = item.get(
                "retry_policy",
                {},
            )

            node.retry_policy = RetryPolicy(
                max_retries=retry.get(
                    "max_retries",
                    1,
                ),
                delay_seconds=retry.get(
                    "delay_seconds",
                    0,
                ),
                exponential_backoff=retry.get(
                    "exponential_backoff",
                    False,
                ),
                max_delay=retry.get(
                    "max_delay",
                    60,
                ),
            )

            condition = item.get(
                "condition",
                {},
            )

            node.condition = StageCondition(
                enabled=condition.get(
                    "enabled",
                    True,
                ),
                expression=condition.get(
                    "expression",
                ),
            )

            node.depends_on = [
                WorkflowStage(stage)
                for stage in item.get(
                    "depends_on",
                    [],
                )
            ]

            node.metadata = item.get(
                "metadata",
                {},
            )

            workflow.add_node(node)

        return workflow

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "Workflow":
        """
        Deserialize workflow from JSON.
        """

        return cls.from_dict(
            json.loads(text)
        )

    # ==================================================================
    # Clone / Copy
    # ==================================================================

    def clone(self) -> "Workflow":
        """
        Create a deep copy of the workflow.
        """

        return Workflow.from_dict(
            self.to_dict()
        )

    # ==================================================================
    # Merge
    # ==================================================================

    def merge(
        self,
        other: "Workflow",
    ) -> None:
        """
        Merge another workflow into this workflow.

        Existing stages are ignored.
        """

        for node in other.nodes:

            if not self.has_node(
                node.stage
            ):
                self.add_node(
                    copy.deepcopy(node)
                )

    # ==================================================================
    # Visualization
    # ==================================================================

    def to_dot(self) -> str:
        """
        Export workflow as Graphviz DOT.
        """

        lines = [
            "digraph Workflow {",
            "    rankdir=LR;",
        ]

        for node in self.enabled_nodes:

            lines.append(
                f'    "{node.stage.value}";'
            )

        for node in self.enabled_nodes:

            for dependency in node.depends_on:

                lines.append(
                    f'    "{dependency.value}" -> "{node.stage.value}";'
                )

        lines.append("}")

        return "\n".join(lines)

    # ==================================================================
    # Summary
    # ==================================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return workflow summary.
        """

        return {
            "id": self.definition.id,
            "name": self.definition.name,
            "version": self.definition.version,
            "nodes": len(
                self.definition.nodes
            ),
            "enabled_nodes": len(
                self.enabled_nodes
            ),
            "root_nodes": [
                node.stage.value
                for node in self.root_nodes()
            ],
            "leaf_nodes": [
                node.stage.value
                for node in self.leaf_nodes()
            ],
        }

    # ==================================================================
    # Representation
    # ==================================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self.definition.nodes
        )

    def __contains__(
        self,
        stage: WorkflowStage,
    ) -> bool:

        return self.has_node(stage)

    def __iter__(
        self,
    ):

        return iter(
            self.execution_order()
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"Workflow("
            f"name={self.definition.name!r}, "
            f"nodes={len(self.definition.nodes)}, "
            f"version={self.definition.version!r})"
        )