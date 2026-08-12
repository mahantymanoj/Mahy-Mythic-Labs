"""
src/providers/image/ideogram_provider.py

Ideogram image-generation provider for Mahy Mythic Labs
Studio OS.

This provider communicates with the Ideogram API for
text-to-image generation.

Responsibilities
----------------
- Ideogram client/API configuration
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


class IdeogramProvider:
    """
    Ideogram image-generation provider.

    The provider uses the Ideogram HTTP API directly rather
    than coupling the rest of Studio OS to Ideogram-specific
    request/response structures.
    """

    DEFAULT_BASE_URL = "https://api.ideogram.ai"

    DEFAULT_MODEL = "V_2"

    GENERATE_ENDPOINT = "/generate"

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
                "Api-Key": self._api_key,
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
        Return the HTTP client.
        """

        return self._client

    @property
    def model(self) -> str:
        """
        Return the configured Ideogram model.
        """

        return self._model

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Verify that an Ideogram API key is configured.

        Ideogram API access can vary by account/API version,
        so this performs a lightweight validation of the
        configured credentials rather than assuming a specific
        account endpoint.
        """

        if not self._api_key:
            logger.error(
                "Ideogram API key is not configured."
            )
            return False

        return True

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Check whether the Ideogram provider is configured.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by Ideogram.
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
        Generate an image using Ideogram.

        Supported parameters
        --------------------
        prompt:
            Image-generation prompt.

        model:
            Ideogram model/version.

        aspect_ratio:
            Requested image aspect ratio.

        magic_prompt:
            Whether Ideogram should enhance the prompt.

        num_images:
            Number of images requested.

        seed:
            Optional generation seed.
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

        aspect_ratio = kwargs.get(
            "aspect_ratio",
            "ASPECT_16_9",
        )

        magic_prompt = kwargs.get(
            "magic_prompt",
            "AUTO",
        )

        num_images = kwargs.get(
            "num_images",
            1,
        )

        seed = kwargs.get(
            "seed",
        )

        if num_images < 1:
            return self._error_response(
                code="INVALID_NUM_IMAGES",
                message=(
                    "num_images must be "
                    "greater than zero."
                ),
                retryable=False,
            )

        payload: dict[str, Any] = {
            "image_request": {
                "prompt": prompt,
                "model": model,
                "aspect_ratio": aspect_ratio,
                "magic_prompt_option": magic_prompt,
                "num_images": num_images,
            }
        }

        if seed is not None:
            payload["image_request"]["seed"] = seed

        try:
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
                        "Ideogram returned no image "
                        "results."
                    ),
                    retryable=False,
                )

            return ProviderResponse(
                success=True,
                provider=ProviderType.IDEOGRAM,
                model=model,
                output=images,
                metadata={
                    "aspect_ratio": aspect_ratio,
                    "num_images": len(images),
                    "magic_prompt": magic_prompt,
                },
            )

        except httpx.HTTPStatusError as exc:
            logger.exception(
                "Ideogram API request failed."
            )

            status_code = (
                exc.response.status_code
            )

            retryable = status_code in {
                408,
                429,
            } or status_code >= 500

            return self._error_response(
                code=f"HTTP_{status_code}",
                message=str(exc),
                retryable=retryable,
            )

        except httpx.RequestError as exc:
            logger.exception(
                "Ideogram network request failed."
            )

            return self._error_response(
                code="CONNECTION_ERROR",
                message=str(exc),
                retryable=True,
            )

        except Exception as exc:
            logger.exception(
                "Ideogram image generation failed."
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
        Extract image URLs from an Ideogram API response.

        Ideogram responses commonly contain image results under
        an `images` collection. Each image may expose its URL
        through an `url` field.

        Returns
        -------
        list[str]
            Normalized image URLs.
        """

        images: list[str] = []

        results = data.get(
            "images",
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
        Build a standardized Ideogram provider error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.IDEOGRAM,
            model=self.model,
            error=ProviderError(
                code=code,
                message=message,
                provider=ProviderType.IDEOGRAM,
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
    ProviderType.IDEOGRAM,
    IdeogramProvider,
)