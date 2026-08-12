"""
src/providers/llm/base_llm_provider.py

Base class for Large Language Model providers.

This module contains LLM-specific behavior shared by concrete
providers such as Anthropic, OpenAI, Google, and xAI.

The universal provider contract remains in:

    src/providers/base_provider.py

Concrete implementations belong in:

    src/providers/llm/
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, AsyncIterator

from ..base_provider import (
    BaseProvider,
    ProviderResponse,
)


class BaseLLMProvider(BaseProvider):
    """
    Base class for LLM providers.

    This class specializes BaseProvider for language-model
    operations while keeping the common provider lifecycle,
    configuration, validation, and error models in BaseProvider.
    """

    # ==================================================================
    # Text Generation
    # ==================================================================

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate text from a prompt.

        Parameters
        ----------
        prompt:
            User prompt.

        **kwargs:
            Provider-specific generation parameters.

        Returns
        -------
        ProviderResponse
            Standardized provider response.
        """

        raise NotImplementedError

    # ==================================================================
    # Streaming
    # ==================================================================

    @abstractmethod
    async def stream_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream generated text.

        Parameters
        ----------
        prompt:
            User prompt.

        **kwargs:
            Provider-specific generation parameters.

        Yields
        ------
        str
            Incremental generated text chunks.
        """

        raise NotImplementedError

    # ==================================================================
    # Embeddings
    # ==================================================================

    @abstractmethod
    async def generate_embeddings(
        self,
        text: str | list[str],
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate vector embeddings.

        Parameters
        ----------
        text:
            Text or collection of texts to embed.

        **kwargs:
            Provider-specific embedding parameters.

        Returns
        -------
        ProviderResponse
            Standardized embedding response.
        """

        raise NotImplementedError

    # ==================================================================
    # Token Counting
    # ==================================================================

    @abstractmethod
    async def count_tokens(
        self,
        text: str,
        model: str | None = None,
    ) -> int:
        """
        Count tokens for a text input.

        Parameters
        ----------
        text:
            Text to tokenize.

        model:
            Optional model name.

        Returns
        -------
        int
            Number of tokens.
        """

        raise NotImplementedError

    # ==================================================================
    # LLM Provider Validation
    # ==================================================================

    def validate_generation_parameters(
        self,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Validate common LLM generation parameters.

        Raises
        ------
        ValueError
            If a parameter is outside its valid range.
        """

        if temperature is not None:
            if not 0.0 <= temperature <= 2.0:
                raise ValueError(
                    "temperature must be between "
                    "0.0 and 2.0."
                )

        if top_p is not None:
            if not 0.0 <= top_p <= 1.0:
                raise ValueError(
                    "top_p must be between "
                    "0.0 and 1.0."
                )

        if max_tokens is not None:
            if max_tokens < 1:
                raise ValueError(
                    "max_tokens must be greater than zero."
                )

    # ==================================================================
    # Prompt Preparation
    # ==================================================================

    def prepare_system_prompt(
        self,
        system: str | None,
    ) -> str | None:
        """
        Normalize an optional system prompt.

        Empty or whitespace-only system prompts are treated
        as absent.
        """

        if system is None:
            return None

        system = system.strip()

        return system or None

    # ==================================================================
    # Common Request Parameters
    # ==================================================================

    def get_generation_parameter(
        self,
        kwargs: dict[str, Any],
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Safely retrieve a generation parameter.

        This helper keeps provider implementations consistent
        when reading optional keyword arguments.
        """

        value = kwargs.get(name)

        if value is None:
            return default

        return value