"""
src/agents/research_agent.py

Research agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Research a topic using a configured LLM/research provider
- Build a structured research request
- Store research output in AgentContext
- Preserve research metadata and source information
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
# Research Agent
# ==============================================================================


class ResearchAgent(BaseAgent):
    """
    Agent responsible for research preparation and execution.

    ResearchAgent does not contain provider-specific API logic.
    The actual LLM/research provider is supplied by the workflow
    or provider-management layer.
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.RESEARCH,
            name="research_agent",
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
        Initialize the ResearchAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "ResearchAgent initialized"
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
        research_type: str = "general",
        depth: str = "standard",
        language: str = "en",
        instructions: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute research for a topic.

        Parameters
        ----------
        topic:
            Subject to research.

        provider:
            LLM/research provider.

        model:
            Optional model override.

        research_type:
            Type of research, for example:
            mythology, history, science, astronomy, general.

        depth:
            Research depth.

        language:
            Desired research language.

        instructions:
            Additional research instructions.

        kwargs:
            Additional provider-specific parameters.

        Returns
        -------
        dict[str, Any]
            Structured research result.
        """

        topic = self._resolve_topic(
            topic
        )

        self._validate_parameters(
            topic=topic,
            depth=depth,
            language=language,
        )

        if provider is None:
            raise RuntimeError(
                "Research provider was not supplied."
            )

        prompt = self._build_research_prompt(
            topic=topic,
            research_type=research_type,
            depth=depth,
            language=language,
            instructions=instructions,
        )

        self.log_info(
            "Starting research for topic=%s provider=%s model=%s",
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
                "Research provider returned no response."
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
                    "Research generation failed.",
                )
                if error is not None
                else "Research generation failed."
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
            "research_type": research_type,
            "depth": depth,
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

        # Store the research result for downstream agents.
        self.set_context_value(
            "research",
            result,
        )

        self.set_context_value(
            "research_output",
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
            "Research completed successfully for topic=%s",
            topic,
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
        Resolve the research topic.

        Explicit topic takes priority.

        If no topic is supplied, attempt to retrieve one
        from AgentContext.
        """

        if topic is not None and topic.strip():
            return topic.strip()

        context_topic = self.get_context_value(
            "research_topic"
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

        raise ValueError(
            "Research topic cannot be empty."
        )

    # ==========================================================================
    # Prompt Construction
    # ==========================================================================

    @staticmethod
    def _build_research_prompt(
        *,
        topic: str,
        research_type: str,
        depth: str,
        language: str,
        instructions: str | None,
    ) -> str:
        """
        Build the research prompt.

        The prompt intentionally asks for structured research
        rather than directly generating a YouTube script.
        """

        prompt = f"""
You are the research specialist for Mahy Mythic Labs Studio OS.

Research Topic:
{topic}

Research Type:
{research_type}

Research Depth:
{depth}

Language:
{language}

Research the topic carefully and produce structured research
that can be consumed by downstream script and storyboard agents.

Separate:

1. Established facts
2. Historical evidence
3. Traditional/mythological accounts
4. Scientific explanations where relevant
5. Different interpretations
6. Important dates, names, places, and terminology
7. Areas of uncertainty or scholarly disagreement
8. Potential misconceptions or popular myths
9. Useful source/reference information

Do not turn the research into a final YouTube script.

Clearly distinguish traditional beliefs from historically or
scientifically established information.
""".strip()

        if instructions:
            prompt += (
                "\n\nAdditional Research Instructions:\n"
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
        depth: str,
        language: str,
    ) -> None:
        """
        Validate research parameters.
        """

        if not topic.strip():
            raise ValueError(
                "Research topic cannot be empty."
            )

        if not depth.strip():
            raise ValueError(
                "Research depth cannot be empty."
            )

        if not language.strip():
            raise ValueError(
                "Research language cannot be empty."
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