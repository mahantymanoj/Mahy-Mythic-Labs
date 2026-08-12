"""
src/providers/image/gemini_image_provider.py

Google Gemini image-generation provider for Mahy Mythic Labs
Studio OS.

This provider uses Google's Gemini API for image generation.

Responsibilities
----------------
- Google GenAI client initialization
- Authentication
- Health checks
- Capability reporting
- Gemini image generation
- Image output normalization
"""

from __future__ import annotations

import base64
import logging
from typing import Any

from google import genai
from google.genai import types

from ..base_provider import (
    ProviderCapability,
    ProviderConfig,
    ProviderError,
    ProviderResponse,
    ProviderType,
)
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class GeminiImageProvider:
    """
    Google Gemini image-generation provider.

    Uses the Google GenAI SDK and Gemini image-capable models.
    """

    DEFAULT_MODEL = "gemini-2.5-flash-image"

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self.config = config

        self._client = genai.Client(
            api_key=config.api_key,
        )

        self._model = (
            config.default_model
            or self.DEFAULT_MODEL
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

    @property
    def model(self) -> str:
        """
        Return the configured Gemini image model.
        """

        return self._model

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Verify Google Gemini credentials.
        """

        try:
            models = self.client.models.list()

            next(
                iter(models),
                None,
            )

            return True

        except Exception:
            logger.exception(
                "Gemini image provider authentication failed."
            )
            return False

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verify Gemini image provider availability.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by Gemini image generation.
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
        Generate an image using Gemini.

        Supported parameters
        --------------------
        model:
            Gemini image-capable model.

        aspect_ratio:
            Requested image aspect ratio.

        number_of_images:
            Number of requested images.

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

        aspect_ratio = kwargs.get(
            "aspect_ratio",
            "16:9",
        )

        number_of_images = kwargs.get(
            "number_of_images",
            1,
        )

        if number_of_images < 1:
            return self._error_response(
                code="INVALID_NUMBER_OF_IMAGES",
                message=(
                    "number_of_images must be "
                    "greater than zero."
                ),
                retryable=False,
            )

        try:
            config_kwargs: dict[str, Any] = {
                "response_modalities": [
                    "IMAGE",
                ],
            }

            image_config = types.ImageConfig(
                aspect_ratio=aspect_ratio,
            )

            config_kwargs[
                "image_config"
            ] = image_config

            config = types.GenerateContentConfig(
                **config_kwargs,
            )

            response = (
                await self.client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
            )

            images = self._extract_images(
                response
            )

            if not images:
                return self._error_response(
                    code="EMPTY_OUTPUT",
                    message=(
                        "Gemini returned no image data."
                    ),
                    retryable=False,
                )

            return ProviderResponse(
                success=True,
                provider=ProviderType.GOOGLE,
                model=model,
                output=images,
                metadata={
                    "aspect_ratio": aspect_ratio,
                    "image_count": len(images),
                },
            )

        except Exception as exc:
            logger.exception(
                "Gemini image generation failed."
            )

            return self._error_response(
                code=exc.__class__.__name__,
                message=str(exc),
                retryable=False,
            )

        # ------------------------------------------------------------------
    # Extract Images
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_images(
        response: Any,
    ) -> list[str]:
        """
        Extract generated image data from a Gemini response.

        Gemini image responses commonly expose image data through
        candidate -> content -> parts -> inline_data.

        The returned values are data URLs so that the rest of
        Studio OS can handle them consistently.
        """

        images: list[str] = []

        candidates = getattr(
            response,
            "candidates",
            None,
        )

        if not candidates:
            return images

        for candidate in candidates:
            content = getattr(
                candidate,
                "content",
                None,
            )

            if content is None:
                continue

            parts = getattr(
                content,
                "parts",
                None,
            )

            if not parts:
                continue

            for part in parts:
                inline_data = getattr(
                    part,
                    "inline_data",
                    None,
                )

                if inline_data is None:
                    continue

                data = getattr(
                    inline_data,
                    "data",
                    None,
                )

                if data is None:
                    continue

                mime_type = getattr(
                    inline_data,
                    "mime_type",
                    "image/png",
                )

                # ------------------------------------------------------
                # Gemini normally returns bytes.
                # ------------------------------------------------------

                if isinstance(data, bytes):
                    encoded = base64.b64encode(
                        data
                    ).decode("ascii")

                    images.append(
                        f"data:{mime_type};base64,{encoded}"
                    )

                # ------------------------------------------------------
                # Handle already encoded string data.
                # ------------------------------------------------------

                elif isinstance(data, str):
                    if data.startswith("data:"):
                        images.append(data)
                    else:
                        images.append(
                            f"data:{mime_type};base64,{data}"
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
        Build a standardized Gemini image error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.GOOGLE,
            model=self.model,
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
        Close the Google GenAI client if the SDK exposes
        a close operation.
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
            f"model={self.model!r})"
        )


# ==============================================================================
# Provider Registration
# ==============================================================================

ProviderFactory.register(
    ProviderType.GOOGLE,
    GeminiImageProvider,
)