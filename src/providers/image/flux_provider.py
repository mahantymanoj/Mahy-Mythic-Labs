"""
src/providers/image/flux_provider.py

FLUX image-generation provider for Mahy Mythic Labs Studio OS.

This provider uses the Replicate API to access FLUX models.

Responsibilities
----------------
- Replicate client initialization
- Authentication
- Health checks
- Capability reporting
- FLUX image generation

Provider-specific API details remain isolated inside this module.
"""

from __future__ import annotations

import logging
from typing import Any

from replicate import AsyncClient
from ..provider_factory import ProviderFactory
from ..base_provider import (
    BaseProvider,
    ProviderCapability,
    ProviderConfig,
    ProviderError,
    ProviderResponse,
    ProviderType,
)

logger = logging.getLogger(__name__)


class FluxProvider(BaseProvider):
    """
    FLUX image-generation provider.

    Uses Replicate as the inference backend.
    """

    DEFAULT_MODEL = (
        "black-forest-labs/flux-schnell"
    )

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        super().__init__(config)

        self._client = AsyncClient(
            api_token=config.api_key,
        )

        self._model = (
            config.default_model
            or self.DEFAULT_MODEL
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def client(self) -> AsyncClient:
        """
        Return the Replicate client.
        """

        return self._client

    @property
    def model(self) -> str:
        """
        Return the configured FLUX model.
        """

        return self._model

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """
        Validate Replicate credentials.
        """

        try:
            # A lightweight account lookup verifies the token.
            await self.client.account.acl()

            return True

        except Exception:
            logger.exception(
                "FLUX/Replicate authentication failed."
            )
            return False

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Check FLUX provider availability.
        """

        return await self.authenticate()

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return capabilities supported by FLUX.
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
        Generate an image using FLUX through Replicate.

        Supported parameters
        --------------------
        model:
            Replicate model identifier.

        aspect_ratio:
            Image aspect ratio, for example "16:9", "1:1",
            "9:16".

        width:
            Optional image width.

        height:
            Optional image height.

        num_outputs:
            Number of images to generate.

        num_inference_steps:
            Number of inference steps.

        guidance_scale:
            Prompt guidance strength.

        seed:
            Optional random seed.

        output_format:
            Output format such as "webp", "png", or "jpg".

        output_quality:
            Output quality for supported formats.
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

        width = kwargs.get(
            "width"
        )

        height = kwargs.get(
            "height"
        )

        num_outputs = kwargs.get(
            "num_outputs",
            1,
        )

        num_inference_steps = kwargs.get(
            "num_inference_steps",
            4,
        )

        guidance_scale = kwargs.get(
            "guidance_scale"
        )

        seed = kwargs.get(
            "seed"
        )

        output_format = kwargs.get(
            "output_format",
            "webp",
        )

        output_quality = kwargs.get(
            "output_quality",
            90,
        )

        # --------------------------------------------------------------
        # Validate parameters
        # --------------------------------------------------------------

        if width is not None and width <= 0:
            return self._error_response(
                code="INVALID_WIDTH",
                message="width must be greater than zero.",
                retryable=False,
            )

        if height is not None and height <= 0:
            return self._error_response(
                code="INVALID_HEIGHT",
                message="height must be greater than zero.",
                retryable=False,
            )

        if num_outputs < 1:
            return self._error_response(
                code="INVALID_NUM_OUTPUTS",
                message="num_outputs must be at least 1.",
                retryable=False,
            )

        if num_inference_steps < 1:
            return self._error_response(
                code="INVALID_STEPS",
                message=(
                    "num_inference_steps must be "
                    "greater than zero."
                ),
                retryable=False,
            )

        if guidance_scale is not None:
            if guidance_scale < 0:
                return self._error_response(
                    code="INVALID_GUIDANCE_SCALE",
                    message=(
                        "guidance_scale cannot be negative."
                    ),
                    retryable=False,
                )

        if seed is not None and seed < 0:
            return self._error_response(
                code="INVALID_SEED",
                message="seed cannot be negative.",
                retryable=False,
            )

        # --------------------------------------------------------------
        # Build Replicate input
        # --------------------------------------------------------------

        input_data: dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "num_outputs": num_outputs,
            "output_format": output_format,
            "output_quality": output_quality,
        }

        if width is not None:
            input_data["width"] = width

        if height is not None:
            input_data["height"] = height

        if num_inference_steps is not None:
            input_data[
                "num_inference_steps"
            ] = num_inference_steps

        if guidance_scale is not None:
            input_data[
                "guidance_scale"
            ] = guidance_scale

        if seed is not None:
            input_data["seed"] = seed

        # --------------------------------------------------------------
        # Generate
        # --------------------------------------------------------------

        try:
            logger.info(
                "Generating FLUX image. model=%s",
                model,
            )

            output = await self.client.run(
                model,
                input=input_data,
            )

            images = self._normalize_output(
                output
            )

            if not images:
                return self._error_response(
                    code="EMPTY_OUTPUT",
                    message=(
                        "FLUX returned no image output."
                    ),
                    retryable=False,
                )

            return ProviderResponse(
                success=True,
                provider=ProviderType.FLUX,
                model=model,
                output=images,
                metadata={
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "num_outputs": len(images),
                    "output_format": output_format,
                },
            )

        except Exception as exc:
            logger.exception(
                "FLUX image generation failed."
            )

            return self._error_response(
                code=exc.__class__.__name__,
                message=str(exc),
                retryable=True,
            )

    # ------------------------------------------------------------------
    # Output Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_output(
        output: Any,
    ) -> list[str]:
        """
        Normalize Replicate output into a list of strings.

        Replicate may return URLs, FileOutput objects,
        or collections of output objects depending on
        the model and SDK version.
        """

        if output is None:
            return []

        if isinstance(output, (str, bytes)):
            return [
                output.decode()
                if isinstance(output, bytes)
                else output
            ]

        if isinstance(output, (list, tuple)):
            results: list[str] = []

            for item in output:
                normalized = FluxProvider._normalize_output(
                    item
                )

                results.extend(normalized)

            return results

        # Replicate FileOutput objects commonly expose
        # a URL through string conversion.
        try:
            value = str(output)

            if value:
                return [value]

        except Exception:
            pass

        return []

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
        Build a standardized provider error response.
        """

        return ProviderResponse(
            success=False,
            provider=ProviderType.FLUX,
            model=self.model,
            error=ProviderError(
                code=code,
                message=message,
                provider=ProviderType.FLUX,
                retryable=retryable,
            ),
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """
        Close the Replicate client.
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
    ProviderType.FLUX,
    FluxProvider,
)