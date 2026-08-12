"""
src/providers/llm/google_provider.py

Google Gemini provider implementation for Studio OS.

This module implements the BaseLLMProvider contract using
Google's Generative AI SDK.

Responsibilities
----------------
- Google client initialization
- Authentication
- Health checks
- Capability reporting
- Provider configuration

Text generation, streaming, embeddings, and token counting
are implemented in subsequent sections.

Python
------
>=3.11
"""

from __future__ import annotations
from ..provider_factory import ProviderFactory
import logging
from typing import Any, AsyncIterator

from google import genai
from google.genai import types

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


class GoogleProvider(BaseLLMProvider):
    """
    Google Gemini implementation of BaseLLMProvider.
    """

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        super().__init__(config)

        client_kwargs: dict[str, Any] = {
            "api_key": config.api_key,
        }

        if config.base_url:
            client_kwargs["http_options"] = {
                "base_url": config.base_url,
            }

        self._client = genai.Client(
            **client_kwargs,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def client(self) -> genai.Client:
        """
        Return the Google GenAI client.
        """

        return self._client

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Validate Google Gemini credentials.

        A lightweight models request is used to verify
        connectivity and credentials.
        """

        try:
            models = self.client.models.list()

            # Consume the iterator so the request is actually
            # evaluated by the SDK.
            next(iter(models), None)

            return True

        except Exception:
            logger.exception(
                "Google Gemini authentication failed."
            )
            return False

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verify Google Gemini availability.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by Google Gemini.
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
        Return models available through Google Gemini.
        """

        try:
            models = self.client.models.list()

            model_names: list[str] = []

            for model in models:
                name = getattr(model, "name", None)

                if not name:
                    continue

                # Google model names are commonly returned as:
                # "models/gemini-2.5-flash"
                if name.startswith("models/"):
                    name = name.removeprefix("models/")

                model_names.append(name)

            return sorted(set(model_names))

        except Exception:
            logger.exception(
                "Failed to list Google Gemini models."
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
        Generate text using Google Gemini.

        Supported keyword arguments
        ---------------------------
        model:
            Gemini model name.

        system:
            Optional system instruction.

        temperature:
            Sampling temperature.

        top_p:
            Nucleus sampling value.

        max_tokens:
            Maximum output tokens.

        Returns
        -------
        ProviderResponse
            Standardized Studio OS response.
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

        self.validate_generation_parameters(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

        generation_config_kwargs: dict[str, Any] = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if top_p is not None:
            generation_config_kwargs["top_p"] = top_p

        config = types.GenerateContentConfig(
            **generation_config_kwargs,
        )

        if system:
            config.system_instruction = system

        try:
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

            text = response.text or ""

            usage = None

            usage_metadata = getattr(
                response,
                "usage_metadata",
                None,
            )

            if usage_metadata is not None:
                prompt_tokens = getattr(
                    usage_metadata,
                    "prompt_token_count",
                    0,
                )

                completion_tokens = getattr(
                    usage_metadata,
                    "candidates_token_count",
                    0,
                )

                total_tokens = getattr(
                    usage_metadata,
                    "total_token_count",
                    0,
                )

                usage = ProviderUsage(
                    prompt_tokens=prompt_tokens or 0,
                    completion_tokens=completion_tokens or 0,
                    total_tokens=total_tokens or 0,
                )

            finish_reason = None

            candidates = getattr(
                response,
                "candidates",
                None,
            )

            if candidates:
                finish_reason = getattr(
                    candidates[0],
                    "finish_reason",
                    None,
                )

                if finish_reason is not None:
                    finish_reason = str(
                        finish_reason
                    )

            return ProviderResponse(
                success=True,
                provider=ProviderType.GOOGLE,
                model=model,
                output=text,
                finish_reason=finish_reason,
                usage=usage,
                metadata={
                    "provider": "google",
                },
            )

        except Exception as exc:
            logger.exception(
                "Google Gemini text generation failed."
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
        Stream generated text from Google Gemini.

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

        self.validate_generation_parameters(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

        generation_config_kwargs: dict[str, Any] = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if top_p is not None:
            generation_config_kwargs["top_p"] = top_p

        config = types.GenerateContentConfig(
            **generation_config_kwargs,
        )

        if system:
            config.system_instruction = system

        try:
            stream = (
                await self.client.aio.models.generate_content_stream(
                    model=model,
                    contents=prompt,
                    config=config,
                )
            )

            async for chunk in stream:
                text = getattr(
                    chunk,
                    "text",
                    None,
                )

                if text:
                    yield text

        except Exception as exc:
            logger.exception(
                "Google Gemini streaming failed."
            )

            raise ProviderError(
                code=exc.__class__.__name__,
                message=str(exc),
                provider=ProviderType.GOOGLE,
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
        Generate embeddings using Google's embedding API.
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

            input_data = [text.strip()]

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
            response = await self.client.aio.models.embed_content(
                model=model,
                contents=input_data,
            )

            embeddings: list[list[float]] = []

            for embedding in response.embeddings:
                values = getattr(
                    embedding,
                    "values",
                    None,
                )

                if values is not None:
                    embeddings.append(
                        list(values)
                    )

            return ProviderResponse(
                success=True,
                provider=ProviderType.GOOGLE,
                model=model,
                output=embeddings,
                metadata={
                    "embedding_count": len(
                        embeddings
                    ),
                },
            )

        except Exception as exc:
            logger.exception(
                "Google Gemini embeddings generation failed."
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
        Count tokens using Google's token-counting API.
        """

        text = text.strip()

        if not text:
            return 0

        resolved_model = self.validate_model(
            model
        )

        try:
            response = (
                await self.client.aio.models.count_tokens(
                    model=resolved_model,
                    contents=text,
                )
            )

            return int(
                getattr(
                    response,
                    "total_tokens",
                    0,
                )
                or 0
            )

        except Exception as exc:
            logger.exception(
                "Google Gemini token counting failed."
            )

            raise ProviderError(
                code=exc.__class__.__name__,
                message=str(exc),
                provider=ProviderType.GOOGLE,
                retryable=False,
            ) from exc
        
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
        Build a standardized Google provider error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.GOOGLE,
            model=model,
            error=ProviderError(
                code=code,
                message=message,
                provider=ProviderType.GOOGLE,
                retryable=retryable,
            ),
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """
        Close the Google GenAI client.

        The SDK client does not require an asynchronous close
        operation in the same way as the OpenAI client.
        """

        close_method = getattr(
            self.client,
            "close",
            None,
        )

        if close_method is not None:
            result = close_method()

            if hasattr(result, "__await__"):
                await result

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a useful provider representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"model={self.default_model!r})"
        )
    

# ==============================================================================
# Provider Registration
# ==============================================================================

ProviderFactory.register(
    ProviderType.GOOGLE,
    GoogleProvider,
)