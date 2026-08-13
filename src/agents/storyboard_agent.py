"""
src/agents/storyboard_agent.py

Storyboard generation agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Convert scripts into structured storyboards
- Consume ScriptAgent output
- Use a configured LLM provider
- Define scenes, shots, visuals, narration, and transitions
- Store storyboard output in AgentContext
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
# Storyboard Agent
# ==============================================================================


class StoryboardAgent(BaseAgent):
    """
    Agent responsible for converting a script into a production storyboard.

    The StoryboardAgent does not generate images or videos directly.

    It produces structured instructions that can later be consumed by:

        StoryboardAgent
              |
              +----> ImageAgent
              |
              +----> VideoAgent
              |
              +----> NarrationAgent
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.STORYBOARD,
            name="storyboard_agent",
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
        Initialize the StoryboardAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "StoryboardAgent initialized"
        )

        return True

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def execute(
        self,
        script: Any | None = None,
        *,
        provider: Any | None = None,
        model: str | None = None,
        title: str | None = None,
        visual_style: str = "realistic cinematic",
        aspect_ratio: str = "16:9",
        target_duration_seconds: int | float | None = None,
        shots_per_scene: int | None = None,
        language: str = "en",
        instructions: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a storyboard from a script.

        Parameters
        ----------
        script:
            Script to convert into a storyboard.

        provider:
            LLM provider used for storyboard generation.

        model:
            Optional model override.

        title:
            Optional video title.

        visual_style:
            Overall visual direction.

        aspect_ratio:
            Target visual aspect ratio.

        target_duration_seconds:
            Target total duration.

        shots_per_scene:
            Optional desired number of shots per scene.

        language:
            Storyboard language.

        instructions:
            Additional storyboard instructions.

        kwargs:
            Additional provider-specific parameters.

        Returns
        -------
        dict[str, Any]
            Structured storyboard-generation result.
        """

        script = self._resolve_script(
            script
        )

        self._validate_parameters(
            script=script,
            visual_style=visual_style,
            aspect_ratio=aspect_ratio,
            language=language,
            target_duration_seconds=(
                target_duration_seconds
            ),
            shots_per_scene=shots_per_scene,
        )

        if provider is None:
            raise RuntimeError(
                "Storyboard provider was not supplied."
            )

        prompt = self._build_storyboard_prompt(
            script=script,
            title=title,
            visual_style=visual_style,
            aspect_ratio=aspect_ratio,
            target_duration_seconds=(
                target_duration_seconds
            ),
            shots_per_scene=shots_per_scene,
            language=language,
            instructions=instructions,
        )

        self.log_info(
            "Generating storyboard using provider=%s model=%s",
            self._provider_name(provider),
            model or "default",
        )

        provider_kwargs: dict[str, Any] = {
            "model": model,
            **kwargs,
        }

        provider_kwargs = {
            key: value
            for key, value in provider_kwargs.items()
            if value is not None
        }

        response = await provider.generate_text(
            prompt,
            **provider_kwargs,
        )

        if response is None:
            raise RuntimeError(
                "Storyboard provider returned no response."
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
                    "Storyboard generation failed.",
                )
                if error is not None
                else "Storyboard generation failed."
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
            "title": title,
            "visual_style": visual_style,
            "aspect_ratio": aspect_ratio,
            "target_duration_seconds": (
                target_duration_seconds
            ),
            "shots_per_scene": shots_per_scene,
            "language": language,
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
            "script": script,
            "prompt": prompt,
            "output": output,
            "usage": getattr(
                response,
                "usage",
                None,
            ),
            "metadata": getattr(
                response,
                "metadata",
                {},
            ),
        }

        # Store complete storyboard result.
        self.set_context_value(
            "storyboard",
            result,
        )

        # Store generated storyboard separately for
        # ImageAgent / VideoAgent / downstream processing.
        self.set_context_value(
            "storyboard_output",
            output,
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
            "Storyboard generation completed successfully."
        )

        return result

    # ==========================================================================
    # Script Resolution
    # ==========================================================================

    def _resolve_script(
        self,
        script: Any | None,
    ) -> Any:
        """
        Resolve the script.

        Explicit script takes priority.

        Otherwise attempt to retrieve ScriptAgent output
        from AgentContext.
        """

        if script is not None:
            return script

        context_script = self.get_context_value(
            "script_output"
        )

        if context_script is not None:
            return context_script

        context_script = self.get_context_value(
            "script"
        )

        if context_script is not None:
            return context_script

        raise RuntimeError(
            "No script was supplied. "
            "Run ScriptAgent before StoryboardAgent "
            "or provide a script explicitly."
        )

    # ==========================================================================
    # Prompt Construction
    # ==========================================================================

    @staticmethod
    def _build_storyboard_prompt(
        *,
        script: Any,
        title: str | None,
        visual_style: str,
        aspect_ratio: str,
        target_duration_seconds: int | float | None,
        shots_per_scene: int | None,
        language: str,
        instructions: str | None,
    ) -> str:
        """
        Build the storyboard-generation prompt.
        """

        title_text = (
            title
            if title
            else "Create an appropriate production title."
        )

        duration_text = (
            f"{target_duration_seconds} seconds"
            if target_duration_seconds is not None
            else "appropriate to the supplied script"
        )

        shot_text = (
            str(shots_per_scene)
            if shots_per_scene is not None
            else "an appropriate number"
        )

        prompt = f"""
You are the storyboard director for Mahy Mythic Labs Studio OS.

Convert the supplied production script into a detailed,
production-ready storyboard.

TITLE
-----
{title_text}

TARGET DURATION
---------------
{duration_text}

VISUAL STYLE
------------
{visual_style}

ASPECT RATIO
------------
{aspect_ratio}

LANGUAGE
--------
{language}

SHOTS PER SCENE
---------------
{shot_text}

SCRIPT
------
{script}

STORYBOARD REQUIREMENTS
-----------------------

Break the script into logical scenes.

For every scene provide:

1. Scene number
2. Scene title
3. Estimated duration
4. Narration associated with the scene
5. Visual description
6. Individual shots
7. Camera framing
8. Camera movement
9. Subject/action
10. Environment/location
11. Lighting
12. Mood
13. Image-generation prompt
14. Video-generation prompt where motion is required
15. Negative visual prompt where useful
16. Transition to the next scene

For every shot, maintain visual continuity.

VISUAL CONTINUITY RULES
-----------------------
- Keep characters visually consistent.
- Keep costumes and important objects consistent.
- Keep environments consistent between connected shots.
- Maintain time-of-day continuity.
- Maintain lighting continuity.
- Maintain geographic continuity.
- Avoid unnecessary changes in character appearance.
- Do not introduce objects that are not justified by the script.

MYTHOLOGY AND HISTORY RULES
---------------------------
- Preserve the distinction between mythology, tradition,
  history, and scientific interpretation.
- Do not invent historical events.
- Do not add unsupported claims.
- Visual enhancements may improve cinematic presentation,
  but must not change the meaning of the story.

CINEMATIC RULES
---------------
- Prefer realistic cinematic visuals.
- Use meaningful camera movements.
- Avoid excessive camera movement.
- Use establishing shots where appropriate.
- Use close-ups for emotional moments.
- Use wide shots for important environments.
- Use controlled transitions.
- Make every shot serve the narrative.

OUTPUT FORMAT
-------------
Return a clearly structured storyboard that downstream
image and video generation systems can process.

Do not rewrite the entire script unnecessarily.
The storyboard should transform the script into visual
production instructions.
""".strip()

        if instructions:
            prompt += (
                "\n\nADDITIONAL STORYBOARD INSTRUCTIONS\n"
                "---------------------------------\n"
                f"{instructions.strip()}"
            )

        return prompt

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_parameters(
        *,
        script: Any,
        visual_style: str,
        aspect_ratio: str,
        language: str,
        target_duration_seconds: int | float | None,
        shots_per_scene: int | None,
    ) -> None:
        """
        Validate storyboard parameters.
        """

        if script is None:
            raise ValueError(
                "Script cannot be empty."
            )

        if isinstance(
            script,
            str,
        ) and not script.strip():
            raise ValueError(
                "Script cannot be empty."
            )

        if not visual_style.strip():
            raise ValueError(
                "visual_style cannot be empty."
            )

        if not aspect_ratio.strip():
            raise ValueError(
                "aspect_ratio cannot be empty."
            )

        if not language.strip():
            raise ValueError(
                "language cannot be empty."
            )

        if (
            target_duration_seconds is not None
            and target_duration_seconds <= 0
        ):
            raise ValueError(
                "target_duration_seconds must be "
                "greater than zero."
            )

        if (
            shots_per_scene is not None
            and shots_per_scene <= 0
        ):
            raise ValueError(
                "shots_per_scene must be greater than zero."
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