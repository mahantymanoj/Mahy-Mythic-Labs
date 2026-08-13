"""
src/agents/video_agent.py

Video generation agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Generate videos from prompts
- Select/use a configured video provider
- Pass generation parameters to the provider
- Support text-to-video and image-to-video workflows
- Store generated asset information in AgentContext
- Return standardized output through BaseAgent

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
# Video Agent
# ==============================================================================


class VideoAgent(BaseAgent):
    """
    Agent responsible for video generation.

    VideoAgent is an orchestration layer between the Studio OS
    workflow and the configured video provider.

    Provider-specific API logic must remain inside the provider
    implementations.
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.VIDEO,
            name="video_agent",
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
        Initialize the VideoAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "VideoAgent initialized"
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
        image: str | None = None,
        image_url: str | None = None,
        output_path: str | None = None,
        duration: int | float | None = None,
        width: int | None = None,
        height: int | None = None,
        aspect_ratio: str | None = None,
        fps: int | None = None,
        negative_prompt: str | None = None,
        seed: int | None = None,
        num_videos: int = 1,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a video.

        Parameters
        ----------
        prompt:
            Text-to-video or image-to-video prompt.

        provider:
            Concrete video provider instance.

        model:
            Optional provider model.

        image:
            Local image path for image-to-video generation.

        image_url:
            Remote image URL for image-to-video generation.

        output_path:
            Optional output path.

        duration:
            Requested video duration in seconds.

        width:
            Requested video width.

        height:
            Requested video height.

        aspect_ratio:
            Requested aspect ratio.

        fps:
            Requested frames per second.

        negative_prompt:
            Optional negative prompt.

        seed:
            Optional generation seed.

        num_videos:
            Number of videos to generate.

        kwargs:
            Additional provider-specific parameters.

        Returns
        -------
        dict[str, Any]
            Standardized video-generation information.
        """

        prompt = self._resolve_prompt(
            prompt
        )

        self._validate_generation_parameters(
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            num_videos=num_videos,
        )

        if provider is None:
            raise RuntimeError(
                "Video provider was not supplied."
            )

        if image and image_url:
            raise ValueError(
                "Provide either 'image' or "
                "'image_url', not both."
            )

        self.log_info(
            "Generating video using provider=%s model=%s",
            self._provider_name(provider),
            model or "default",
        )

        provider_kwargs: dict[str, Any] = {
            "model": model,
            "image": image,
            "image_url": image_url,
            "output_path": output_path,
            "duration": duration,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "fps": fps,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_videos": num_videos,
            **kwargs,
        }

        # Remove parameters that were not supplied.
        provider_kwargs = {
            key: value
            for key, value in provider_kwargs.items()
            if value is not None
        }

        response = await provider.generate_video(
            prompt,
            **provider_kwargs,
        )

        if response is None:
            raise RuntimeError(
                "Video provider returned no response."
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
                    "Video generation failed.",
                )
                if error is not None
                else "Video generation failed."
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
            "image": image,
            "image_url": image_url,
            "duration": duration,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "fps": fps,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_videos": num_videos,
        }

        # Store the latest video result in workflow context.
        self.set_context_value(
            "video_generation",
            result,
        )

        self.set_metadata(
            "last_provider",
            self._provider_name(provider),
        )

        self.set_metadata(
            "last_model",
            model,
        )

        self.log_info(
            "Video generation completed successfully."
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
        Resolve the video generation prompt.

        Explicit prompt takes priority.

        If no explicit prompt is supplied, the agent attempts
        to retrieve a prompt from AgentContext.
        """

        if prompt is not None and prompt.strip():
            return prompt.strip()

        context_prompt = self.get_context_value(
            "video_prompt"
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
            "Video prompt cannot be empty."
        )

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_generation_parameters(
        *,
        duration: int | float | None,
        width: int | None,
        height: int | None,
        fps: int | None,
        num_videos: int,
    ) -> None:
        """
        Validate common video-generation parameters.
        """

        if duration is not None and duration <= 0:
            raise ValueError(
                "duration must be greater than zero."
            )

        if width is not None and width <= 0:
            raise ValueError(
                "width must be greater than zero."
            )

        if height is not None and height <= 0:
            raise ValueError(
                "height must be greater than zero."
            )

        if fps is not None and fps <= 0:
            raise ValueError(
                "fps must be greater than zero."
            )

        if num_videos < 1:
            raise ValueError(
                "num_videos must be at least 1."
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