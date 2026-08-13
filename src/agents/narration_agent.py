"""
src/agents/narration_agent.py

Narration / text-to-speech agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Convert narration scripts into speech
- Use a configured TTS provider
- Support voice/model configuration
- Store generated narration information in AgentContext
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
# Narration Agent
# ==============================================================================


class NarrationAgent(BaseAgent):
    """
    Agent responsible for narration and text-to-speech generation.

    Provider-specific TTS/API logic belongs inside the provider layer.
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.NARRATION,
            name="narration_agent",
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
        Initialize the NarrationAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "NarrationAgent initialized"
        )

        return True

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def execute(
        self,
        text: str | None = None,
        *,
        provider: Any | None = None,
        model: str | None = None,
        voice: str | None = None,
        language: str | None = None,
        output_path: str | None = None,
        speed: float | None = None,
        pitch: float | None = None,
        format: str | None = None,
        sample_rate: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate narration audio.

        Parameters
        ----------
        text:
            Narration text.

        provider:
            Concrete TTS provider.

        model:
            Optional TTS model.

        voice:
            Voice identifier.

        language:
            Narration language.

        output_path:
            Optional audio output path.

        speed:
            Speech speed.

        pitch:
            Voice pitch where supported.

        format:
            Audio format such as mp3 or wav.

        sample_rate:
            Requested audio sample rate.

        kwargs:
            Additional provider-specific options.
        """

        text = self._resolve_text(text)

        self._validate_parameters(
            text=text,
            speed=speed,
            pitch=pitch,
            sample_rate=sample_rate,
        )

        if provider is None:
            raise RuntimeError(
                "Narration provider was not supplied."
            )

        self.log_info(
            "Generating narration using provider=%s model=%s voice=%s",
            self._provider_name(provider),
            model or "default",
            voice or "default",
        )

        provider_kwargs: dict[str, Any] = {
            "model": model,
            "voice": voice,
            "language": language,
            "output_path": output_path,
            "speed": speed,
            "pitch": pitch,
            "format": format,
            "sample_rate": sample_rate,
            **kwargs,
        }

        # Remove parameters that were not supplied.
        provider_kwargs = {
            key: value
            for key, value in provider_kwargs.items()
            if value is not None
        }

        response = await provider.generate_audio(
            text,
            **provider_kwargs,
        )

        if response is None:
            raise RuntimeError(
                "Narration provider returned no response."
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
                    "Narration generation failed.",
                )
                if error is not None
                else "Narration generation failed."
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
            "text": text,
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
            "voice": voice,
            "language": language,
            "output": output,
            "output_path": output_path,
            "speed": speed,
            "pitch": pitch,
            "format": format,
            "sample_rate": sample_rate,
        }

        # Store narration result in workflow context.
        self.set_context_value(
            "narration_generation",
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

        self.set_metadata(
            "last_voice",
            voice,
        )

        self.log_info(
            "Narration generation completed successfully."
        )

        return result

    # ==========================================================================
    # Text Resolution
    # ==========================================================================

    def _resolve_text(
        self,
        text: str | None,
    ) -> str:
        """
        Resolve narration text.

        Explicit text takes priority.

        If text is not supplied, attempt to retrieve it from
        AgentContext.
        """

        if text is not None and text.strip():
            return text.strip()

        context_text = self.get_context_value(
            "narration_text"
        )

        if isinstance(
            context_text,
            str,
        ) and context_text.strip():
            return context_text.strip()

        context_text = self.get_context_value(
            "script"
        )

        if isinstance(
            context_text,
            str,
        ) and context_text.strip():
            return context_text.strip()

        context_text = self.get_context_value(
            "text"
        )

        if isinstance(
            context_text,
            str,
        ) and context_text.strip():
            return context_text.strip()

        raise ValueError(
            "Narration text cannot be empty."
        )

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_parameters(
        *,
        text: str,
        speed: float | None,
        pitch: float | None,
        sample_rate: int | None,
    ) -> None:
        """
        Validate common narration parameters.
        """

        if not text.strip():
            raise ValueError(
                "Narration text cannot be empty."
            )

        if speed is not None and speed <= 0:
            raise ValueError(
                "speed must be greater than zero."
            )

        if sample_rate is not None and sample_rate <= 0:
            raise ValueError(
                "sample_rate must be greater than zero."
            )

        # Pitch ranges differ between providers, so we only
        # validate that it is numeric here.
        if pitch is not None and not isinstance(
            pitch,
            (int, float),
        ):
            raise ValueError(
                "pitch must be numeric."
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