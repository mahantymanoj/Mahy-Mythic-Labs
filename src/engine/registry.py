"""
src/engine/registry.py

Central dependency registry for Mahy Mythic Labs Studio OS.

The registry manages:

- Agents
- AI Providers
- Workflows
- Pipelines
- Plugins
- Factories
- Singleton instances

Python
------
>=3.11
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ==============================================================================
# Registry Item
# ==============================================================================


@dataclass(slots=True)
class RegistryItem:
    """
    One registered component.
    """

    name: str

    factory: Callable[..., Any]

    singleton: bool = False

    instance: Any | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Registry
# ==============================================================================


class Registry:
    """
    Central dependency registry.
    """

    def __init__(self) -> None:

        self._agents: dict[
            str,
            RegistryItem,
        ] = {}

        self._providers: dict[
            str,
            RegistryItem,
        ] = {}

        self._workflows: dict[
            str,
            RegistryItem,
        ] = {}

        self._pipelines: dict[
            str,
            RegistryItem,
        ] = {}

        self._plugins: dict[
            str,
            RegistryItem,
        ] = {}

        logger.info(
            "Registry initialized."
        )

    # ==================================================================
    # Generic Registration
    # ==================================================================

    def _register(
        self,
        registry: dict[str, RegistryItem],
        *,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Internal registration helper.
        """

        if name in registry:

            raise ValueError(
                f"'{name}' is already registered."
            )

        registry[name] = RegistryItem(
            name=name,
            factory=factory,
            singleton=singleton,
            metadata=metadata or {},
        )

        logger.info(
            "Registered: %s",
            name,
        )

    # ==================================================================
    # Agent Registration
    # ==================================================================

    def register_agent(
        self,
        *,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self._register(
            self._agents,
            name=name,
            factory=factory,
            singleton=singleton,
            metadata=metadata,
        )

    # ==================================================================
    # Provider Registration
    # ==================================================================

    def register_provider(
        self,
        *,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self._register(
            self._providers,
            name=name,
            factory=factory,
            singleton=singleton,
            metadata=metadata,
        )

    # ==================================================================
    # Workflow Registration
    # ==================================================================

    def register_workflow(
        self,
        *,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self._register(
            self._workflows,
            name=name,
            factory=factory,
            singleton=singleton,
            metadata=metadata,
        )

    # ==================================================================
    # Pipeline Registration
    # ==================================================================

    def register_pipeline(
        self,
        *,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self._register(
            self._pipelines,
            name=name,
            factory=factory,
            singleton=singleton,
            metadata=metadata,
        )

        # ==================================================================
    # Generic Resolve
    # ==================================================================

    def _resolve(
        self,
        registry: dict[str, RegistryItem],
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Resolve an object from the registry.
        """

        if name not in registry:

            raise KeyError(
                f"'{name}' is not registered."
            )

        item = registry[name]

        if item.singleton:

            if item.instance is None:

                logger.info(
                    "Creating singleton: %s",
                    name,
                )

                item.instance = item.factory(
                    *args,
                    **kwargs,
                )

            return item.instance

        logger.debug(
            "Creating instance: %s",
            name,
        )

        return item.factory(
            *args,
            **kwargs,
        )

    # ==================================================================
    # Agent Resolution
    # ==================================================================

    def get_agent(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._agents,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Provider Resolution
    # ==================================================================

    def get_provider(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._providers,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Workflow Resolution
    # ==================================================================

    def get_workflow(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._workflows,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Pipeline Resolution
    # ==================================================================

    def get_pipeline(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._pipelines,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Plugin Registration
    # ==================================================================

    def register_plugin(
        self,
        *,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self._register(
            self._plugins,
            name=name,
            factory=factory,
            singleton=singleton,
            metadata=metadata,
        )

    def get_plugin(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._plugins,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Exists
    # ==================================================================

    def has_agent(
        self,
        name: str,
    ) -> bool:

        return name in self._agents

    def has_provider(
        self,
        name: str,
    ) -> bool:

        return name in self._providers

    def has_workflow(
        self,
        name: str,
    ) -> bool:

        return name in self._workflows

    def has_pipeline(
        self,
        name: str,
    ) -> bool:

        return name in self._pipelines

    def has_plugin(
        self,
        name: str,
    ) -> bool:

        return name in self._plugins

    # ==================================================================
    # Removal
    # ==================================================================

    def unregister_agent(
        self,
        name: str,
    ) -> None:

        self._agents.pop(
            name,
            None,
        )

    def unregister_provider(
        self,
        name: str,
    ) -> None:

        self._providers.pop(
            name,
            None,
        )

    def unregister_workflow(
        self,
        name: str,
    ) -> None:

        self._workflows.pop(
            name,
            None,
        )

    def unregister_pipeline(
        self,
        name: str,
    ) -> None:

        self._pipelines.pop(
            name,
            None,
        )

    def unregister_plugin(
        self,
        name: str,
    ) -> None:

        self._plugins.pop(
            name,
            None,
        )

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, int]:

        return {

            "agents":
                len(self._agents),

            "providers":
                len(self._providers),

            "workflows":
                len(self._workflows),

            "pipelines":
                len(self._pipelines),

            "plugins":
                len(self._plugins),
        }

        # ==================================================================
    # Generic Resolve
    # ==================================================================

    def _resolve(
        self,
        registry: dict[str, RegistryItem],
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Resolve an object from the registry.
        """

        if name not in registry:

            raise KeyError(
                f"'{name}' is not registered."
            )

        item = registry[name]

        if item.singleton:

            if item.instance is None:

                logger.info(
                    "Creating singleton: %s",
                    name,
                )

                item.instance = item.factory(
                    *args,
                    **kwargs,
                )

            return item.instance

        logger.debug(
            "Creating instance: %s",
            name,
        )

        return item.factory(
            *args,
            **kwargs,
        )

    # ==================================================================
    # Agent Resolution
    # ==================================================================

    def get_agent(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._agents,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Provider Resolution
    # ==================================================================

    def get_provider(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._providers,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Workflow Resolution
    # ==================================================================

    def get_workflow(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._workflows,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Pipeline Resolution
    # ==================================================================

    def get_pipeline(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._pipelines,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Plugin Registration
    # ==================================================================

    def register_plugin(
        self,
        *,
        name: str,
        factory: Callable[..., Any],
        singleton: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self._register(
            self._plugins,
            name=name,
            factory=factory,
            singleton=singleton,
            metadata=metadata,
        )

    def get_plugin(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self._resolve(
            self._plugins,
            name,
            *args,
            **kwargs,
        )

    # ==================================================================
    # Exists
    # ==================================================================

    def has_agent(
        self,
        name: str,
    ) -> bool:

        return name in self._agents

    def has_provider(
        self,
        name: str,
    ) -> bool:

        return name in self._providers

    def has_workflow(
        self,
        name: str,
    ) -> bool:

        return name in self._workflows

    def has_pipeline(
        self,
        name: str,
    ) -> bool:

        return name in self._pipelines

    def has_plugin(
        self,
        name: str,
    ) -> bool:

        return name in self._plugins

    # ==================================================================
    # Removal
    # ==================================================================

    def unregister_agent(
        self,
        name: str,
    ) -> None:

        self._agents.pop(
            name,
            None,
        )

    def unregister_provider(
        self,
        name: str,
    ) -> None:

        self._providers.pop(
            name,
            None,
        )

    def unregister_workflow(
        self,
        name: str,
    ) -> None:

        self._workflows.pop(
            name,
            None,
        )

    def unregister_pipeline(
        self,
        name: str,
    ) -> None:

        self._pipelines.pop(
            name,
            None,
        )

    def unregister_plugin(
        self,
        name: str,
    ) -> None:

        self._plugins.pop(
            name,
            None,
        )

    # ==================================================================
    # Statistics
    # ==================================================================

    def statistics(
        self,
    ) -> dict[str, int]:

        return {

            "agents":
                len(self._agents),

            "providers":
                len(self._providers),

            "workflows":
                len(self._workflows),

            "pipelines":
                len(self._pipelines),

            "plugins":
                len(self._plugins),
        }

    