"""
src/providers/image/pollinations_provider.py

Pollinations image-generation provider for Mahy Mythic Labs
Studio OS.

Pollinations provides a simple HTTP-based image-generation
interface. This provider keeps the HTTP details isolated from
the rest of Studio OS.

Responsibilities
----------------
- Pollinations configuration
- Authentication/configuration checks
- Health checks
- Capability reporting
- Image generation
- Generated image URL normalization
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import httpx

from ..base_provider import (
    ProviderCapability,
    ProviderConfig,
    ProviderError,
    ProviderResponse,
    ProviderType,
)
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class PollinationsProvider:
    """
    Pollinations image-generation provider.

    Pollinations can be used without a conventional API key for
    supported public endpoints, so authentication is treated as
    an optional configuration check.
    """

    DEFAULT_BASE_URL = (
        "https://image.pollinations.ai"
    )

    DEFAULT_MODEL = "flux"

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self.config = config

        self._api_key = config.api_key

        self._base_url = (
            config.base_url
            or self.DEFAULT_BASE_URL
        ).rstrip("/")

        self._model = (
            config.default_model
            or self.DEFAULT_MODEL
        )

        self._client = httpx.AsyncClient(
            timeout=config.timeout,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def client(self) -> httpx.AsyncClient:
        """
        Return the HTTP client.
        """

        return self._client

    @property
    def model(self) -> str:
        """
        Return the configured Pollinations model.
        """

        return self._model

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Validate Pollinations configuration.

        Pollinations may support public image generation without
        an API key, so absence of an API key does not automatically
        mean authentication failure.
        """

        return bool(self._base_url)

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Check Pollinations availability.

        The health check uses the configured base URL and performs
        a lightweight HTTP request.
        """

        try:
            response = await self.client.get(
                self._base_url,
                timeout=10.0,
            )

            return response.status_code < 500

        except httpx.RequestError:
            logger.exception(
                "Pollinations health check failed."
            )
            return False

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by Pollinations.
        """

        return {
            ProviderCapability.IMAGE,
        }

    # ------------------------------------------------------------------
    # Image Generation
    # ------------------------------------------------------------------

    async def generate_image(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate an image through Pollinations.

        Supported parameters
        --------------------
        prompt:
            Image-generation prompt.

        model:
            Pollinations model.

        width:
            Requested image width.

        height:
            Requested image height.

        seed:
            Optional deterministic seed.

        nologo:
            Whether to request no logo.

        enhance:
            Whether to request prompt enhancement.

        Returns
        -------
        ProviderResponse
            Standardized response containing the generated
            image URL.
        """

        prompt = prompt.strip()

        if not prompt:
            return self._error_response(
                code="INVALID_INPUT",
                message="Image prompt cannot be empty.",
                retryable=False,
            )

        model = (
            kwargs.get("model")
            or self.model
        )

        width = kwargs.get(
            "width",
            1024,
        )

        height = kwargs.get(
            "height",
            1024,
        )

        seed = kwargs.get(
            "seed",
        )

        nologo = kwargs.get(
            "nologo",
            True,
        )

        enhance = kwargs.get(
            "enhance",
            False,
        )

        if width <= 0:
            return self._error_response(
                code="INVALID_WIDTH",
                message="width must be greater than zero.",
                retryable=False,
            )

        if height <= 0:
            return self._error_response(
                code="INVALID_HEIGHT",
                message="height must be greater than zero.",
                retryable=False,
            )

        encoded_prompt = quote(
            prompt,
            safe="",
        )

        url = (
            f"{self._base_url}/prompt/"
            f"{encoded_prompt}"
        )

        params: dict[str, Any] = {
            "model": model,
            "width": width,
            "height": height,
            "nologo": str(nologo).lower(),
            "enhance": str(enhance).lower(),
        }

        if seed is not None:
            params["seed"] = seed

        try:
            logger.info(
                "Generating image through Pollinations. "
                "model=%s",
                model,
            )

            response = await self.client.get(
                url,
                params=params,
            )

            response.raise_for_status()

            image_url = str(
                response.url
            )

            return ProviderResponse(
                success=True,
                provider=ProviderType.POLLINATIONS,
                model=model,
                output=[
                    image_url,
                ],
                metadata={
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "enhance": enhance,
                },
            )

        except httpx.HTTPStatusError as exc:
            status_code = (
                exc.response.status_code
            )

            logger.exception(
                "Pollinations image request failed."
            )

            return self._error_response(
                code=f"HTTP_{status_code}",
                message=str(exc),
                retryable=(
                    status_code == 429
                    or status_code >= 500
                ),
            )

        except httpx.RequestError as exc:
            logger.exception(
                "Pollinations network request failed."
            )

            return self._error_response(
                code="CONNECTION_ERROR",
                message=str(exc),
                retryable=True,
            )

        except Exception as exc:
            logger.exception(
                "Pollinations image generation failed."
            )

            return self._error_response(
                code=exc.__class__.__name__,
                message=str(exc),
                retryable=False,
            )

        # ------------------------------------------------------------------
    # Error Response
    # ------------------------------------------------------------------

    def _error_response(
        self,
        *,
        code: str,
        message: str,
        retryable: bool,
    ) -> ProviderResponse:
        """
        Build a standardized Pollinations provider error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.POLLINATIONS,
            model=self.model,
            error=ProviderError(
                code=code,
                message=message,
                provider=ProviderType.POLLINATIONS,
                retryable=retryable,
            ),
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """
        Close the underlying HTTP client.
        """

        await self.client.aclose()

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a useful provider representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"model={self.model!r})"
        )

# ==============================================================================
# Provider Registration
# ==============================================================================

ProviderFactory.register(
    ProviderType.POLLINATIONS,
    PollinationsProvider,
)