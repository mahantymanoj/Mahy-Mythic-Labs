"""
src/providers/image/recraft_provider.py

Recraft image-generation provider for Mahy Mythic Labs
Studio OS.

This provider communicates with the Recraft API for
text-to-image generation.

Responsibilities
----------------
- Recraft API configuration
- Authentication
- Health checks
- Capability reporting
- Image generation
- Output normalization
"""

from __future__ import annotations

import logging
from typing import Any

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


class RecraftProvider:
    """
    Recraft image-generation provider.

    The provider isolates Recraft-specific HTTP/API details
    from the rest of Studio OS.
    """

    DEFAULT_BASE_URL = (
        "https://external.api.recraft.ai"
    )

    DEFAULT_MODEL = "recraftv3"

    GENERATE_ENDPOINT = "/v1/images/generations"

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
            base_url=self._base_url,
            headers={
                "Authorization": (
                    f"Bearer {self._api_key}"
                ),
                "Content-Type": "application/json",
            },
            timeout=config.timeout,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def client(self) -> httpx.AsyncClient:
        """
        Return the Recraft HTTP client.
        """

        return self._client

    @property
    def model(self) -> str:
        """
        Return the configured Recraft model.
        """

        return self._model

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Validate Recraft API configuration.

        A lightweight configuration check is used here because
        API capabilities and available endpoints can vary between
        Recraft API versions.
        """

        if not self._api_key:
            logger.error(
                "Recraft API key is not configured."
            )
            return False

        return True

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Check whether the Recraft provider is configured.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by Recraft.
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
        Generate an image using Recraft.

        Supported parameters
        --------------------
        prompt:
            Image-generation prompt.

        model:
            Recraft model identifier.

        size:
            Requested image size.

        n:
            Number of images.

        style:
            Optional Recraft style identifier.

        Returns
        -------
        ProviderResponse
            Standardized image-generation response.
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

        size = kwargs.get(
            "size",
            "1024x1024",
        )

        number_of_images = kwargs.get(
            "n",
            1,
        )

        style = kwargs.get(
            "style",
        )

        if number_of_images < 1:
            return self._error_response(
                code="INVALID_NUMBER_OF_IMAGES",
                message=(
                    "n must be greater than zero."
                ),
                retryable=False,
            )

        payload: dict[str, Any] = {
            "prompt": prompt,
            "model": model,
            "size": size,
            "n": number_of_images,
        }

        if style:
            payload["style"] = style

        try:
            logger.info(
                "Generating image through Recraft. "
                "model=%s",
                model,
            )

            response = await self.client.post(
                self.GENERATE_ENDPOINT,
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

            images = self._extract_images(
                data
            )

            if not images:
                return self._error_response(
                    code="EMPTY_OUTPUT",
                    message=(
                        "Recraft returned no image results."
                    ),
                    retryable=False,
                )

            return ProviderResponse(
                success=True,
                provider=ProviderType.RECRAFT,
                model=model,
                output=images,
                metadata={
                    "size": size,
                    "image_count": len(images),
                    "style": style,
                },
            )

        except httpx.HTTPStatusError as exc:
            status_code = (
                exc.response.status_code
            )

            logger.exception(
                "Recraft API request failed."
            )

            retryable = (
                status_code == 408
                or status_code == 429
                or status_code >= 500
            )

            return self._error_response(
                code=f"HTTP_{status_code}",
                message=str(exc),
                retryable=retryable,
            )

        except httpx.RequestError as exc:
            logger.exception(
                "Recraft network request failed."
            )

            return self._error_response(
                code="CONNECTION_ERROR",
                message=str(exc),
                retryable=True,
            )

        except Exception as exc:
            logger.exception(
                "Recraft image generation failed."
            )

            return self._error_response(
                code=exc.__class__.__name__,
                message=str(exc),
                retryable=False,
            )
        # ------------------------------------------------------------------
    # Output Extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_images(
        data: dict[str, Any],
    ) -> list[str]:
        """
        Extract generated image URLs from a Recraft response.

        Expected response structure:

            {
                "data": [
                    {
                        "url": "https://..."
                    }
                ]
            }

        Returns
        -------
        list[str]
            Normalized image URLs.
        """

        images: list[str] = []

        results = data.get(
            "data",
            [],
        )

        if not isinstance(results, list):
            return images

        for item in results:
            if not isinstance(item, dict):
                continue

            url = item.get("url")

            if isinstance(url, str) and url.strip():
                images.append(
                    url.strip()
                )

        return images

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
        Build a standardized Recraft provider error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.RECRAFT,
            model=self.model,
            error=ProviderError(
                code=code,
                message=message,
                provider=ProviderType.RECRAFT,
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
    ProviderType.RECRAFT,
    RecraftProvider,
)