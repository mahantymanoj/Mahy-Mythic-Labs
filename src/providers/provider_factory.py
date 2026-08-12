"""
src/providers/provider_factory.py

Factory responsible for creating AI provider instances.

The ProviderFactory decouples the rest of Studio OS from
provider-specific implementations.

Example
-------
config = ProviderConfig(
    provider=ProviderType.OPENAI,
    api_key="..."
)

provider = ProviderFactory.create(config)

response = await provider.generate_text("Hello")

Python
------
>=3.11
"""

from __future__ import annotations

from typing import Type

from .base_provider import (
    BaseProvider,
    ProviderConfig,
    ProviderType,
)

# ==============================================================================
# Provider Factory
# ==============================================================================


class ProviderFactory:
    """
    Creates provider instances.

    Providers register themselves with this factory.
    """

    _providers: dict[
        ProviderType,
        Type[BaseProvider],
    ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    @classmethod
    def register(
        cls,
        provider_type: ProviderType,
        provider_class: Type[BaseProvider],
    ) -> None:
        """
        Register a provider implementation.
        """

        cls._providers[provider_type] = provider_class

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @classmethod
    def registered_providers(
        cls,
    ) -> list[ProviderType]:
        """
        Return all registered provider types.
        """

        return sorted(
            cls._providers.keys(),
            key=lambda item: item.value,
        )

    @classmethod
    def is_registered(
        cls,
        provider_type: ProviderType,
    ) -> bool:
        """
        Check whether a provider is registered.
        """

        return provider_type in cls._providers

        # ------------------------------------------------------------------
    # Provider Creation
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        config: ProviderConfig,
    ) -> BaseProvider:
        """
        Create a provider instance from configuration.

        Raises
        ------
        ValueError
            If the provider is not registered.
        """

        provider_class = cls._providers.get(
            config.provider
        )

        if provider_class is None:
            raise ValueError(
                f"Provider '{config.provider.value}' "
                "is not registered."
            )

        return provider_class(config)

    # ------------------------------------------------------------------
    # Registry Management
    # ------------------------------------------------------------------

    @classmethod
    def unregister(
        cls,
        provider_type: ProviderType,
    ) -> bool:
        """
        Remove a provider registration.

        Returns
        -------
        bool
            True if removed, False otherwise.
        """

        return (
            cls._providers.pop(
                provider_type,
                None,
            )
            is not None
        )

    @classmethod
    def clear(
        cls,
    ) -> None:
        """
        Remove every registered provider.

        Primarily useful for testing.
        """

        cls._providers.clear()

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    @classmethod
    def get_provider_class(
        cls,
        provider_type: ProviderType,
    ) -> type[BaseProvider]:
        """
        Return the registered provider class.

        Raises
        ------
        ValueError
            If the provider is not registered.
        """

        provider_class = cls._providers.get(
            provider_type
        )

        if provider_class is None:
            raise ValueError(
                f"Provider '{provider_type.value}' "
                "is not registered."
            )

        return provider_class

        # ------------------------------------------------------------------
    # Registry Information
    # ------------------------------------------------------------------

    @classmethod
    def provider_count(cls) -> int:
        """
        Return the number of registered providers.
        """

        return len(cls._providers)

    @classmethod
    def registry(cls) -> dict[ProviderType, type[BaseProvider]]:
        """
        Return a shallow copy of the provider registry.
        """

        return dict(cls._providers)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    @classmethod
    def summary(cls) -> str:
        """
        Return a human-readable summary of the registry.
        """

        if not cls._providers:
            return "ProviderFactory(registered=0)"

        providers = ", ".join(
            provider.value
            for provider in sorted(
                cls._providers.keys(),
                key=lambda item: item.value,
            )
        )

        return (
            f"ProviderFactory("
            f"registered={len(cls._providers)}, "
            f"providers=[{providers}])"
        )

    @classmethod
    def __repr__(cls) -> str:
        return cls.summary()
