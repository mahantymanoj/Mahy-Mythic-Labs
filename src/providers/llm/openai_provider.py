"""
src/providers/llm/openai_provider.py

OpenAI provider implementation for Studio OS.

This module implements the BaseLLMProvider contract using
the official OpenAI Python SDK.

Responsibilities
----------------
- OpenAI client initialization
- Authentication
- Health checks
- Capability reporting
- Model discovery

Text generation, streaming, embeddings, token counting,
and resource cleanup are implemented in subsequent sections.

Python
------
>=3.11

Dependency
----------
openai
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from openai import (
    APIError,
    APIConnectionError,
    AuthenticationError,
    AsyncOpenAI,
    RateLimitError,
)

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


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI implementation of BaseLLMProvider.
    """

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        super().__init__(config)

        client_kwargs: dict[str, Any] = {
            "api_key": config.api_key,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
        }

        if config.base_url:
            client_kwargs["base_url"] = config.base_url

        if config.organization:
            client_kwargs["organization"] = config.organization

        self._client = AsyncOpenAI(
            **client_kwargs,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def client(self) -> AsyncOpenAI:
        """
        Return the underlying OpenAI async client.
        """

        return self._client

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Validate OpenAI credentials.

        A lightweight models request is used to verify that the
        configured API key can communicate with OpenAI.
        """

        try:
            await self.client.models.list()
            return True

        except AuthenticationError:
            logger.error(
                "OpenAI authentication failed."
            )
            return False

        except Exception:
            logger.exception(
                "Unexpected OpenAI authentication error."
            )
            return False

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verify that OpenAI is reachable and credentials are valid.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by this provider.
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
        Return models available to the configured OpenAI account.

        Only model IDs that can reasonably be used for the LLM
        provider are returned.
        """

        try:
            response = await self.client.models.list()

            models = [
                model.id
                for model in response.data
                if model.id
            ]

            return sorted(models)

        except APIError:
            logger.exception(
                "OpenAI model listing failed."
            )
            return []

        except Exception:
            logger.exception(
                "Unexpected error while listing OpenAI models."
            )
            return []

    # ------------------------------------------------------------------
    # Text Generation
    # ------------------------------------------------------------------

    async def generate_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate text using an OpenAI chat model.

        Supported keyword arguments
        ---------------------------
        model:
            OpenAI model name.

        system:
            Optional system instruction.

        temperature:
            Sampling temperature.

        max_tokens:
            Maximum output tokens.

        top_p:
            Nucleus sampling value.

        seed:
            Optional deterministic seed where supported.

        Returns
        -------
        ProviderResponse
            Standardized Studio OS provider response.
        """

        prompt = self.validate_prompt(
            prompt
        )

        model = self.validate_model(
            kwargs.get("model")
        )

        system = kwargs.get(
            "system"
        )

        temperature = kwargs.get(
            "temperature",
            0.7,
        )

        max_tokens = kwargs.get(
            "max_tokens",
            4096,
        )

        top_p = kwargs.get(
            "top_p"
        )

        seed = kwargs.get(
            "seed"
        )

        messages: list[dict[str, str]] = []

        if system:
            messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        request_kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if top_p is not None:
            request_kwargs["top_p"] = top_p

        if seed is not None:
            request_kwargs["seed"] = seed

        try:
            response = await self.client.chat.completions.create(
                **request_kwargs
            )

            text = ""

            if response.choices:
                message = response.choices[0].message

                if message.content:
                    text = message.content

            usage = None

            if response.usage is not None:
                usage = ProviderUsage(
                    prompt_tokens=(
                        response.usage.prompt_tokens
                    ),
                    completion_tokens=(
                        response.usage.completion_tokens
                    ),
                    total_tokens=(
                        response.usage.total_tokens
                    ),
                )

            return ProviderResponse(
                success=True,
                provider=ProviderType.OPENAI,
                model=model,
                output=text,
                finish_reason=(
                    response.choices[0].finish_reason
                    if response.choices
                    else None
                ),
                usage=usage,
                metadata={
                    "response_id": response.id,
                },
            )

        except AuthenticationError as exc:
            logger.error(
                "OpenAI authentication error during text generation."
            )

            return self._error_response(
                model=model,
                code="AUTHENTICATION_ERROR",
                message=str(exc),
                retryable=False,
            )

        except RateLimitError as exc:
            logger.warning(
                "OpenAI rate limit reached."
            )

            return self._error_response(
                model=model,
                code="RATE_LIMIT_ERROR",
                message=str(exc),
                retryable=True,
            )

        except APIConnectionError as exc:
            logger.warning(
                "OpenAI connection error."
            )

            return self._error_response(
                model=model,
                code="CONNECTION_ERROR",
                message=str(exc),
                retryable=True,
            )

        except APIError as exc:
            logger.exception(
                "OpenAI API error during text generation."
            )

            return self._error_response(
                model=model,
                code="API_ERROR",
                message=str(exc),
                retryable=False,
            )

        except Exception as exc:
            logger.exception(
                "Unexpected OpenAI text generation error."
            )

            return self._error_response(
                model=model,
                code=exc.__class__.__name__,
                message=str(exc),
                retryable=False,
            )

        # ------------------------------------------------------------------
    # Streaming Text Generation
    # ------------------------------------------------------------------

    async def stream_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream generated text from OpenAI.

        Yields
        ------
        str
            Incremental text chunks.
        """

        prompt = self.validate_prompt(prompt)

        model = self.validate_model(
            kwargs.get("model")
        )

        system = kwargs.get("system")

        temperature = kwargs.get(
            "temperature",
            0.7,
        )

        max_tokens = kwargs.get(
            "max_tokens",
            4096,
        )

        top_p = kwargs.get(
            "top_p"
        )

        seed = kwargs.get(
            "seed"
        )

        messages: list[dict[str, str]] = []

        if system:
            messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        request_kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if top_p is not None:
            request_kwargs["top_p"] = top_p

        if seed is not None:
            request_kwargs["seed"] = seed

        try:
            stream = await self.client.chat.completions.create(
                **request_kwargs
            )

            async for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    yield delta.content

        except AuthenticationError as exc:
            logger.error(
                "OpenAI authentication error during streaming."
            )

            raise ProviderError(
                code="AUTHENTICATION_ERROR",
                message=str(exc),
                provider=ProviderType.OPENAI,
                retryable=False,
            ) from exc

        except RateLimitError as exc:
            logger.warning(
                "OpenAI rate limit reached during streaming."
            )

            raise ProviderError(
                code="RATE_LIMIT_ERROR",
                message=str(exc),
                provider=ProviderType.OPENAI,
                retryable=True,
            ) from exc

        except APIConnectionError as exc:
            logger.warning(
                "OpenAI connection error during streaming."
            )

            raise ProviderError(
                code="CONNECTION_ERROR",
                message=str(exc),
                provider=ProviderType.OPENAI,
                retryable=True,
            ) from exc

        except APIError as exc:
            logger.exception(
                "OpenAI API error during streaming."
            )

            raise ProviderError(
                code="API_ERROR",
                message=str(exc),
                provider=ProviderType.OPENAI,
                retryable=False,
            ) from exc

        except Exception as exc:
            logger.exception(
                "Unexpected OpenAI streaming error."
            )

            raise ProviderError(
                code=exc.__class__.__name__,
                message=str(exc),
                provider=ProviderType.OPENAI,
                retryable=False,
            ) from exc

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    async def generate_embeddings(
        self,
        text: str | list[str],
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate embeddings using OpenAI.

        Parameters
        ----------
        text:
            Single text string or a list of strings.

        model:
            Embedding model. Defaults to the provider's
            configured default model.
        """

        model = self.validate_model(
            kwargs.get("model")
        )

        if isinstance(text, str):
            if not text.strip():
                return self._error_response(
                    model=model,
                    code="INVALID_INPUT",
                    message="Text cannot be empty.",
                    retryable=False,
                )

            input_data: str | list[str] = text

        else:
            input_data = [
                item.strip()
                for item in text
                if item and item.strip()
            ]

            if not input_data:
                return self._error_response(
                    model=model,
                    code="INVALID_INPUT",
                    message="Text list cannot be empty.",
                    retryable=False,
                )

        try:
            response = await self.client.embeddings.create(
                model=model,
                input=input_data,
            )

            embeddings = [
                item.embedding
                for item in response.data
            ]

            usage = None

            if response.usage is not None:
                usage = ProviderUsage(
                    prompt_tokens=(
                        response.usage.prompt_tokens
                    ),
                    completion_tokens=0,
                    total_tokens=(
                        response.usage.total_tokens
                    ),
                )

            return ProviderResponse(
                success=True,
                provider=ProviderType.OPENAI,
                model=model,
                output=embeddings,
                usage=usage,
                metadata={
                    "embedding_count": len(embeddings),
                },
            )

        except AuthenticationError as exc:
            return self._error_response(
                model=model,
                code="AUTHENTICATION_ERROR",
                message=str(exc),
                retryable=False,
            )

        except RateLimitError as exc:
            return self._error_response(
                model=model,
                code="RATE_LIMIT_ERROR",
                message=str(exc),
                retryable=True,
            )

        except APIConnectionError as exc:
            return self._error_response(
                model=model,
                code="CONNECTION_ERROR",
                message=str(exc),
                retryable=True,
            )

        except APIError as exc:
            logger.exception(
                "OpenAI embeddings API error."
            )

            return self._error_response(
                model=model,
                code="API_ERROR",
                message=str(exc),
                retryable=False,
            )

        except Exception as exc:
            logger.exception(
                "Unexpected OpenAI embeddings error."
            )

            return self._error_response(
                model=model,
                code=exc.__class__.__name__,
                message=str(exc),
                retryable=False,
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
        Estimate the number of tokens in a text.

        OpenAI does not expose a universal remote token-counting
        endpoint for all models. A local tokenizer is therefore
        preferred when available.

        Falls back to a conservative approximation when the
        tokenizer package/model encoding is unavailable.
        """

        text = text.strip()

        if not text:
            return 0

        resolved_model = self.validate_model(model)

        try:
            import tiktoken

            try:
                encoding = tiktoken.encoding_for_model(
                    resolved_model
                )
            except KeyError:
                encoding = tiktoken.get_encoding(
                    "cl100k_base"
                )

            return len(
                encoding.encode(text)
            )

        except ImportError:
            logger.warning(
                "tiktoken is not installed. "
                "Using approximate token count."
            )

        except Exception:
            logger.exception(
                "OpenAI token counting failed. "
                "Using approximate token count."
            )

        # Conservative approximation:
        # roughly 1 token per 4 characters for English text.
        return max(
            1,
            len(text) // 4,
        )

        # ------------------------------------------------------------------
    # Error Response
    # ------------------------------------------------------------------

    @staticmethod
    def _error_response(
        model: str,
        code: str,
        message: str,
        retryable: bool,
    ) -> ProviderResponse:
        """
        Build a standardized provider error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.OPENAI,
            model=model,
            error=ProviderError(
                code=code,
                message=message,
                provider=ProviderType.OPENAI,
                retryable=retryable,
            ),
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """
        Close the underlying OpenAI client.
        """

        await self.client.close()

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a useful representation of the provider.
        """

        return (
            f"{self.__class__.__name__}("
            f"model={self.default_model!r})"
        )


# ==============================================================================
# Provider Registration
# ==============================================================================

from ..provider_factory import ProviderFactory

ProviderFactory.register(
    ProviderType.OPENAI,
    OpenAIProvider,
)