"""
src/agents/image_agent.py

Image generation agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Generate images from prompts
- Select an image provider
- Pass generation parameters to the provider
- Store generated asset information in AgentContext
- Support image generation workflows
- Return standardized AgentResult through BaseAgent

Python
------
>= 3.11
"""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import (
    AgentContext,
    AgentType,
    BaseAgent,
)


logger = logging.getLogger(__name__)


# ==============================================================================
# Image Agent
# ==============================================================================


class ImageAgent(BaseAgent):
    """
    Agent responsible for image generation.

    The ImageAgent acts as an orchestration layer between the
    Studio OS workflow and the configured image provider.

    It should not contain provider-specific API logic.
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.IMAGE,
            name="image_agent",
            config=config,
        )

    # ==========================================================================
    # Initialization
    # ==========================================================================

    async def initialize(
        self,
        context: AgentContext | None = None,
    ) -> bool:
        """
        Initialize the ImageAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "ImageAgent initialized"
        )

        return True

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def execute(
        self,
        prompt: str | None = None,
        *,
        provider: Any | None = None,
        model: str | None = None,
        output_path: str | None = None,
        width: int | None = None,
        height: int | None = None,
        aspect_ratio: str | None = None,
        negative_prompt: str | None = None,
        seed: int | None = None,
        num_images: int = 1,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate an image.

        Parameters
        ----------
        prompt:
            Image generation prompt.

        provider:
            Concrete image provider instance.

        model:
            Optional model override.

        output_path:
            Optional location where the generated image
            should be saved.

        width:
            Requested image width.

        height:
            Requested image height.

        aspect_ratio:
            Requested aspect ratio.

        negative_prompt:
            Optional negative prompt.

        seed:
            Optional generation seed.

        num_images:
            Number of images to generate.

        kwargs:
            Additional provider-specific parameters.

        Returns
        -------
        dict
            Standardized image generation information.
        """

        prompt = self._resolve_prompt(
            prompt
        )

        self._validate_generation_parameters(
            num_images=num_images,
            width=width,
            height=height,
        )

        if provider is None:
            raise RuntimeError(
                "Image provider was not supplied."
            )

        self.log_info(
            "Generating image using provider=%s model=%s",
            getattr(
                provider,
                "provider_type",
                "unknown",
            ),
            model or "default",
        )

        provider_kwargs: dict[str, Any] = {
            "model": model,
            "output_path": output_path,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_images": num_images,
            **kwargs,
        }

        # Remove parameters that were not provided.
        provider_kwargs = {
            key: value
            for key, value in provider_kwargs.items()
            if value is not None
        }

        response = await provider.generate_image(
            prompt,
            **provider_kwargs,
        )

        if response is None:
            raise RuntimeError(
                "Image provider returned no response."
            )

        success = getattr(
            response,
            "success",
            False,
        )

        if not success:
            error = getattr(
                response,
                "error",
                None,
            )

            error_message = (
                getattr(
                    error,
                    "message",
                    "Image generation failed.",
                )
                if error is not None
                else "Image generation failed."
            )

            raise RuntimeError(
                error_message
            )

        output = getattr(
            response,
            "output",
            None,
        )

        result = {
            "prompt": prompt,
            "provider": self._provider_name(
                provider
            ),
            "model": (
                model
                or getattr(
                    response,
                    "model",
                    None,
                )
            ),
            "output": output,
            "output_path": output_path,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_images": num_images,
        }

        # Store result in shared workflow context.
        self.set_context_value(
            "image_generation",
            result,
        )

        self.set_metadata(
            "last_provider",
            self._provider_name(
                provider
            ),
        )

        self.set_metadata(
            "last_model",
            model,
        )

        self.log_info(
            "Image generation completed successfully."
        )

        return result

    # ==========================================================================
    # Prompt Resolution
    # ==========================================================================

    def _resolve_prompt(
        self,
        prompt: str | None,
    ) -> str:
        """
        Resolve the image prompt.

        Explicit prompt takes priority. If no prompt is supplied,
        the agent attempts to retrieve one from AgentContext.
        """

        if prompt is not None and prompt.strip():
            return prompt.strip()

        context_prompt = self.get_context_value(
            "image_prompt"
        )

        if isinstance(
            context_prompt,
            str,
        ) and context_prompt.strip():
            return context_prompt.strip()

        context_prompt = self.get_context_value(
            "prompt"
        )

        if isinstance(
            context_prompt,
            str,
        ) and context_prompt.strip():
            return context_prompt.strip()

        raise ValueError(
            "Image prompt cannot be empty."
        )

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_generation_parameters(
        *,
        num_images: int,
        width: int | None,
        height: int | None,
    ) -> None:
        """
        Validate common image-generation parameters.
        """

        if num_images < 1:
            raise ValueError(
                "num_images must be at least 1."
            )

        if width is not None and width <= 0:
            raise ValueError(
                "width must be greater than zero."
            )

        if height is not None and height <= 0:
            raise ValueError(
                "height must be greater than zero."
            )

    # ==========================================================================
    # Provider Helpers
    # ==========================================================================

    @staticmethod
    def _provider_name(
        provider: Any,
    ) -> str:
        """
        Return a readable provider name.
        """

        provider_type = getattr(
            provider,
            "provider_type",
            None,
        )

        if provider_type is not None:
            value = getattr(
                provider_type,
                "value",
                None,
            )

            if value:
                return str(value)

            return str(provider_type)

        return provider.__class__.__name__