"""
src/agents/script_agent.py

Script generation agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Generate scripts from research
- Consume ResearchAgent output
- Use a configured LLM provider
- Apply script-generation instructions
- Store generated script in AgentContext
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
# Script Agent
# ==============================================================================


class ScriptAgent(BaseAgent):
    """
    Agent responsible for generating video scripts.

    ScriptAgent does not contain provider-specific API logic.
    The actual LLM provider is supplied by the workflow/provider
    management layer.
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.SCRIPT,
            name="script_agent",
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
        Initialize the ScriptAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "ScriptAgent initialized"
        )

        return True

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def execute(
        self,
        topic: str | None = None,
        *,
        provider: Any | None = None,
        model: str | None = None,
        research: Any | None = None,
        title: str | None = None,
        duration_minutes: int | float | None = None,
        language: str = "en",
        tone: str = "cinematic",
        audience: str = "general",
        script_type: str = "youtube",
        instructions: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a video script.

        Parameters
        ----------
        topic:
            Video topic.

        provider:
            LLM provider used for script generation.

        model:
            Optional model override.

        research:
            Research data. If omitted, the agent attempts to
            retrieve research_output from AgentContext.

        title:
            Optional working title.

        duration_minutes:
            Target video duration.

        language:
            Script language.

        tone:
            Desired storytelling tone.

        audience:
            Target audience.

        script_type:
            Type of script, e.g. youtube, documentary,
            short, educational.

        instructions:
            Additional script instructions.

        kwargs:
            Additional provider-specific parameters.

        Returns
        -------
        dict[str, Any]
            Structured script-generation result.
        """

        topic = self._resolve_topic(
            topic
        )

        research = self._resolve_research(
            research
        )

        self._validate_parameters(
            topic=topic,
            language=language,
            tone=tone,
            audience=audience,
            script_type=script_type,
            duration_minutes=duration_minutes,
        )

        if provider is None:
            raise RuntimeError(
                "Script provider was not supplied."
            )

        prompt = self._build_script_prompt(
            topic=topic,
            research=research,
            title=title,
            duration_minutes=duration_minutes,
            language=language,
            tone=tone,
            audience=audience,
            script_type=script_type,
            instructions=instructions,
        )

        self.log_info(
            "Generating script for topic=%s provider=%s model=%s",
            topic,
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
                "Script provider returned no response."
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
                    "Script generation failed.",
                )
                if error is not None
                else "Script generation failed."
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
            "topic": topic,
            "title": title,
            "duration_minutes": duration_minutes,
            "language": language,
            "tone": tone,
            "audience": audience,
            "script_type": script_type,
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
            "research": research,
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

        # Store the complete result.
        self.set_context_value(
            "script",
            result,
        )

        # Store the actual generated script separately
        # for downstream agents.
        self.set_context_value(
            "script_output",
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
            "Script generation completed successfully."
        )

        return result

    # ==========================================================================
    # Topic Resolution
    # ==========================================================================

    def _resolve_topic(
        self,
        topic: str | None,
    ) -> str:
        """
        Resolve the script topic.
        """

        if topic is not None and topic.strip():
            return topic.strip()

        context_topic = self.get_context_value(
            "script_topic"
        )

        if isinstance(
            context_topic,
            str,
        ) and context_topic.strip():
            return context_topic.strip()

        context_topic = self.get_context_value(
            "topic"
        )

        if isinstance(
            context_topic,
            str,
        ) and context_topic.strip():
            return context_topic.strip()

        research = self.get_context_value(
            "research"
        )

        if isinstance(
            research,
            dict,
        ):
            research_topic = research.get(
                "topic"
            )

            if isinstance(
                research_topic,
                str,
            ) and research_topic.strip():
                return research_topic.strip()

        raise ValueError(
            "Script topic cannot be empty."
        )

    # ==========================================================================
    # Research Resolution
    # ==========================================================================

    def _resolve_research(
        self,
        research: Any | None,
    ) -> Any:
        """
        Resolve research input.

        Explicit research takes priority.

        Otherwise attempt to retrieve research output
        from AgentContext.
        """

        if research is not None:
            return research

        context_research = self.get_context_value(
            "research_output"
        )

        if context_research is not None:
            return context_research

        context_research = self.get_context_value(
            "research"
        )

        if context_research is not None:
            return context_research

        raise RuntimeError(
            "No research data was supplied. "
            "Run ResearchAgent before ScriptAgent "
            "or provide research explicitly."
        )

    # ==========================================================================
    # Prompt Construction
    # ==========================================================================

    @staticmethod
    def _build_script_prompt(
        *,
        topic: str,
        research: Any,
        title: str | None,
        duration_minutes: int | float | None,
        language: str,
        tone: str,
        audience: str,
        script_type: str,
        instructions: str | None,
    ) -> str:
        """
        Build the script-generation prompt.
        """

        duration_text = (
            f"{duration_minutes} minutes"
            if duration_minutes is not None
            else "appropriate for the topic"
        )

        title_text = (
            title
            if title
            else "Create an appropriate working title."
        )

        prompt = f"""
You are the script-writing specialist for
Mahy Mythic Labs Studio OS.

Create a high-quality video script using the research
provided below.

TOPIC
-----
{topic}

WORKING TITLE
-------------
{title_text}

TARGET DURATION
---------------
{duration_text}

LANGUAGE
--------
{language}

TONE
----
{tone}

TARGET AUDIENCE
---------------
{audience}

SCRIPT TYPE
-----------
{script_type}

RESEARCH
--------
{research}

SCRIPT REQUIREMENTS
-------------------
1. Base factual claims on the supplied research.
2. Clearly distinguish mythology, tradition, history,
   science, and interpretation where applicable.
3. Do not invent historical facts.
4. Do not present speculation as established fact.
5. Create a strong opening hook.
6. Maintain narrative flow throughout the script.
7. Use clear sections/scenes.
8. Make narration natural for voice generation.
9. Avoid unnecessarily long sentences.
10. Include transitions between major sections.
11. End with an appropriate conclusion.
12. Do not include unsupported claims merely to make
    the story more dramatic.

Return a production-ready script rather than a research report.
""".strip()

        if instructions:
            prompt += (
                "\n\nADDITIONAL SCRIPT INSTRUCTIONS\n"
                "-----------------------------\n"
                f"{instructions.strip()}"
            )

        return prompt

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_parameters(
        *,
        topic: str,
        language: str,
        tone: str,
        audience: str,
        script_type: str,
        duration_minutes: int | float | None,
    ) -> None:
        """
        Validate script-generation parameters.
        """

        if not topic.strip():
            raise ValueError(
                "Script topic cannot be empty."
            )

        if not language.strip():
            raise ValueError(
                "Script language cannot be empty."
            )

        if not tone.strip():
            raise ValueError(
                "Script tone cannot be empty."
            )

        if not audience.strip():
            raise ValueError(
                "Script audience cannot be empty."
            )

        if not script_type.strip():
            raise ValueError(
                "Script type cannot be empty."
            )

        if (
            duration_minutes is not None
            and duration_minutes <= 0
        ):
            raise ValueError(
                "duration_minutes must be greater than zero."
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