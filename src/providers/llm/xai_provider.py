"""
src/providers/llm/xai_provider.py

xAI Grok provider implementation for Studio OS.

xAI provides an OpenAI-compatible API, so this provider uses
the OpenAI AsyncOpenAI client with the xAI API base URL.

Responsibilities
----------------
- xAI client initialization
- Authentication
- Health checks
- Capability reporting
- Model discovery

Text generation, streaming, embeddings, token counting,
and cleanup are implemented in subsequent sections.

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
    APIConnectionError,
    APIError,
    AsyncOpenAI,
    AuthenticationError,
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
from ..provider_factory import ProviderFactory
from .base_llm_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class XAIProvider(BaseLLMProvider):
    """
    xAI Grok implementation of BaseLLMProvider.
    """

    DEFAULT_BASE_URL = "https://api.x.ai/v1"

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        super().__init__(config)

        client_kwargs: dict[str, Any] = {
            "api_key": config.api_key,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
            "base_url": (
                config.base_url
                or self.DEFAULT_BASE_URL
            ),
        }

        self._client = AsyncOpenAI(
            **client_kwargs,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def client(self) -> AsyncOpenAI:
        """
        Return the underlying xAI-compatible client.
        """

        return self._client

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Validate xAI credentials.

        The models endpoint is used as a lightweight
        authentication and connectivity check.
        """

        try:
            await self.client.models.list()
            return True

        except AuthenticationError:
            logger.error(
                "xAI authentication failed."
            )
            return False

        except Exception:
            logger.exception(
                "Unexpected xAI authentication error."
            )
            return False

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verify xAI availability.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by xAI.
        """

        return {
            ProviderCapability.TEXT,
        }

        # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------

    async def list_models(
        self,
    ) -> list[str]:
        """
        Return models available through xAI.
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
                "xAI model listing failed."
            )
            return []

        except Exception:
            logger.exception(
                "Unexpected error while listing xAI models."
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
        Generate text using an xAI Grok model.

        Supported keyword arguments
        ---------------------------
        model:
            xAI model name.

        system:
            Optional system instruction.

        temperature:
            Sampling temperature.

        top_p:
            Nucleus sampling value.

        max_tokens:
            Maximum output tokens.

        seed:
            Optional deterministic seed where supported.
        """

        prompt = self.validate_prompt(
            prompt
        )

        model = self.validate_model(
            kwargs.get("model")
        )

        system = self.prepare_system_prompt(
            kwargs.get("system")
        )

        temperature = kwargs.get(
            "temperature",
            0.7,
        )

        top_p = kwargs.get(
            "top_p"
        )

        max_tokens = kwargs.get(
            "max_tokens",
            4096,
        )

        seed = kwargs.get(
            "seed"
        )

        self.validate_generation_parameters(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
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

            finish_reason = None

            if response.choices:
                finish_reason = (
                    response.choices[0].finish_reason
                )

            return ProviderResponse(
                success=True,
                provider=ProviderType.XAI,
                model=model,
                output=text,
                finish_reason=finish_reason,
                usage=usage,
                metadata={
                    "response_id": response.id,
                },
            )

        except AuthenticationError as exc:
            logger.error(
                "xAI authentication error during text generation."
            )

            return self._error_response(
                model=model,
                code="AUTHENTICATION_ERROR",
                message=str(exc),
                retryable=False,
            )

        except RateLimitError as exc:
            logger.warning(
                "xAI rate limit reached."
            )

            return self._error_response(
                model=model,
                code="RATE_LIMIT_ERROR",
                message=str(exc),
                retryable=True,
            )

        except APIConnectionError as exc:
            logger.warning(
                "xAI connection error."
            )

            return self._error_response(
                model=model,
                code="CONNECTION_ERROR",
                message=str(exc),
                retryable=True,
            )

        except APIError as exc:
            logger.exception(
                "xAI API error during text generation."
            )

            return self._error_response(
                model=model,
                code="API_ERROR",
                message=str(exc),
                retryable=False,
            )

        except Exception as exc:
            logger.exception(
                "Unexpected xAI text generation error."
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
        Stream generated text from xAI.

        Yields
        ------
        str
            Incremental generated text chunks.
        """

        prompt = self.validate_prompt(prompt)

        model = self.validate_model(
            kwargs.get("model")
        )

        system = self.prepare_system_prompt(
            kwargs.get("system")
        )

        temperature = kwargs.get(
            "temperature",
            0.7,
        )

        top_p = kwargs.get(
            "top_p"
        )

        max_tokens = kwargs.get(
            "max_tokens",
            4096,
        )

        seed = kwargs.get(
            "seed"
        )

        self.validate_generation_parameters(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
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
                "xAI authentication error during streaming."
            )

            raise ProviderError(
                code="AUTHENTICATION_ERROR",
                message=str(exc),
                provider=ProviderType.XAI,
                retryable=False,
            ) from exc

        except RateLimitError as exc:
            logger.warning(
                "xAI rate limit reached during streaming."
            )

            raise ProviderError(
                code="RATE_LIMIT_ERROR",
                message=str(exc),
                provider=ProviderType.XAI,
                retryable=True,
            ) from exc

        except APIConnectionError as exc:
            logger.warning(
                "xAI connection error during streaming."
            )

            raise ProviderError(
                code="CONNECTION_ERROR",
                message=str(exc),
                provider=ProviderType.XAI,
                retryable=True,
            ) from exc

        except APIError as exc:
            logger.exception(
                "xAI API error during streaming."
            )

            raise ProviderError(
                code="API_ERROR",
                message=str(exc),
                provider=ProviderType.XAI,
                retryable=False,
            ) from exc

        except Exception as exc:
            logger.exception(
                "Unexpected xAI streaming error."
            )

            raise ProviderError(
                code=exc.__class__.__name__,
                message=str(exc),
                provider=ProviderType.XAI,
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
        xAI does not currently provide an embeddings endpoint
        through the OpenAI-compatible API used by this provider.

        Returns a standardized unsupported-operation response.
        """

        model = self.validate_model(
            kwargs.get("model")
        )

        return self._error_response(
            model=model,
            code="NOT_SUPPORTED",
            message=(
                "xAI embeddings are not supported "
                "by this provider implementation."
            ),
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
        Estimate token count locally.

        xAI does not expose a universal token-counting endpoint
        through the OpenAI-compatible interface, so tiktoken is
        used when available.

        If tiktoken is unavailable, a conservative approximation
        is returned.
        """

        text = text.strip()

        if not text:
            return 0

        resolved_model = self.validate_model(
            model
        )

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
                "Using approximate xAI token count."
            )

        except Exception:
            logger.exception(
                "xAI token counting failed. "
                "Using approximate token count."
            )

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
        Build a standardized xAI provider error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.XAI,
            model=model,
            error=ProviderError(
                code=code,
                message=message,
                provider=ProviderType.XAI,
                retryable=retryable,
            ),
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """
        Close the underlying OpenAI-compatible xAI client.
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

ProviderFactory.register(
    ProviderType.XAI,
    XAIProvider,
)