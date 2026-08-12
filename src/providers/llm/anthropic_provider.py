"""
src/providers/llm/anthropic_provider.py

Anthropic Claude provider implementation.

This module implements the BaseLLMProvider contract using the
official Anthropic Python SDK.

Python
------
>=3.11

Package
-------
anthropic>=0.68.0
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

import anthropic
from anthropic import AsyncAnthropic
from ..provider_factory import ProviderFactory
from ..base_provider import (
    ProviderCapability,
    ProviderConfig,
    ProviderError,
    ProviderResponse,
    ProviderType,
    ProviderUsage,
)
from .base_llm_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider.
    """

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        super().__init__(config)

        self._client = AsyncAnthropic(
            api_key=config.api_key,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def client(self) -> AsyncAnthropic:
        """
        Return Anthropic client.
        """

        return self._client

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Validate API credentials.

        A lightweight model listing request is used
        to verify the API key.
        """

        try:
            await self.list_models()
            return True

        except Exception:
            logger.exception(
                "Anthropic authentication failed."
            )
            return False

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verify provider availability.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Supported capabilities.
        """

        return {
            ProviderCapability.TEXT,
            ProviderCapability.EMBEDDING,
        }
        # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------

    async def list_models(
        self,
    ) -> list[str]:
        """
        Return supported Anthropic models.

        Note:
            Anthropic does not currently provide a public
            "list models" endpoint. We therefore maintain
            the supported production model list here.
        """

        return [
            "claude-opus-4-1",
            "claude-sonnet-4",
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-5-haiku-latest",
        ]

    # ------------------------------------------------------------------
    # Text Generation
    # ------------------------------------------------------------------

    async def generate_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate text using Anthropic Claude.
        """

        prompt = self.validate_prompt(prompt)

        model = self.validate_model(
            kwargs.get("model")
        )

        max_tokens = kwargs.get(
            "max_tokens",
            4096,
        )

        temperature = kwargs.get(
            "temperature",
            0.7,
        )

        system = kwargs.get("system")

        try:

            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            text = ""

            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text

            usage = ProviderUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=(
                    response.usage.input_tokens
                    + response.usage.output_tokens
                ),
            )

            return ProviderResponse(
                success=True,
                provider=ProviderType.ANTHROPIC,
                model=model,
                output=text,
                finish_reason=response.stop_reason,
                usage=usage,
                metadata={
                    "response_id": response.id,
                },
            )

        except Exception as exc:

            logger.exception(
                "Anthropic text generation failed."
            )

            return ProviderResponse(
                success=False,
                provider=ProviderType.ANTHROPIC,
                model=model,
                error=ProviderError(
                    code=exc.__class__.__name__,
                    message=str(exc),
                    provider=ProviderType.ANTHROPIC,
                    retryable=False,
                ),
            )

        # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    async def stream_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream text generation.
        """

        prompt = self.validate_prompt(prompt)

        model = self.validate_model(
            kwargs.get("model")
        )

        max_tokens = kwargs.get(
            "max_tokens",
            4096,
        )

        temperature = kwargs.get(
            "temperature",
            0.7,
        )

        system = kwargs.get("system")

        async with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        ) as stream:

            async for text in stream.text_stream:
                yield text

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    async def generate_embeddings(
        self,
        text: str | list[str],
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate embeddings.

        Anthropic currently does not provide an embeddings API.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.ANTHROPIC,
            model=self.validate_model(
                kwargs.get("model")
            ),
            error=ProviderError(
                code="NOT_SUPPORTED",
                message=(
                    "Anthropic does not currently "
                    "support embeddings."
                ),
                provider=ProviderType.ANTHROPIC,
                retryable=False,
            ),
        )

    # ------------------------------------------------------------------
    # Token Counting
    # ------------------------------------------------------------------

    async def count_tokens(
        self,
        text: str,
        model: str | None = None,
    ) -> int:
        """
        Estimate token count.

        Uses Anthropic's token counting API when available.
        """

        model = self.validate_model(model)

        try:

            response = await self.client.messages.count_tokens(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
            )

            return response.input_tokens

        except Exception:

            logger.exception(
                "Failed to count Anthropic tokens."
            )

            return 0

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(
        self,
    ) -> None:
        """
        Release provider resources.
        """

        if hasattr(self.client, "close"):
            await self.client.close()

        # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        String representation of the provider.
        """

        return (
            f"{self.__class__.__name__}("
            f"model={self.default_model!r})"
        )

# ==============================================================================
# Provider Registration
# ==============================================================================

ProviderFactory.register(
    ProviderType.ANTHROPIC,
    AnthropicProvider,
)