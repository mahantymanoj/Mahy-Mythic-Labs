"""
src/agents/seo_agent.py

SEO optimization agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Generate YouTube titles
- Generate descriptions
- Generate keywords and tags
- Generate hashtags
- Generate thumbnail direction
- Generate SEO metadata
- Consume ScriptAgent / StoryboardAgent output
- Store SEO output in AgentContext
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
# SEO Agent
# ==============================================================================


class SEOAgent(BaseAgent):
    """
    Agent responsible for YouTube SEO optimization.

    SEOAgent prepares metadata for publishing but does NOT
    upload or publish videos.

    Typical flow:

        ScriptAgent
             |
             v
        StoryboardAgent
             |
             v
          SEOAgent
             |
             v
      PublishingAgent
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.SEO,
            name="seo_agent",
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
        Initialize the SEOAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "SEOAgent initialized"
        )

        return True

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def execute(
        self,
        content: Any | None = None,
        *,
        provider: Any | None = None,
        model: str | None = None,
        topic: str | None = None,
        title: str | None = None,
        platform: str = "youtube",
        language: str = "en",
        audience: str = "general",
        category: str = "Education",
        generate_multiple_titles: bool = True,
        title_count: int = 5,
        tag_count: int = 20,
        hashtag_count: int = 8,
        include_thumbnail_prompt: bool = True,
        instructions: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate SEO metadata.

        Parameters
        ----------
        content:
            Script, storyboard, or final content.

        provider:
            LLM provider used for SEO generation.

        model:
            Optional model override.

        topic:
            Video topic.

        title:
            Existing title, if available.

        platform:
            Target platform. Currently optimized for YouTube.

        language:
            Metadata language.

        audience:
            Target audience.

        category:
            YouTube content category.

        generate_multiple_titles:
            Generate multiple title candidates.

        title_count:
            Number of title candidates.

        tag_count:
            Maximum number of tags.

        hashtag_count:
            Number of hashtags.

        include_thumbnail_prompt:
            Generate thumbnail creative direction.

        instructions:
            Additional SEO instructions.

        kwargs:
            Additional provider-specific parameters.

        Returns
        -------
        dict[str, Any]
            Structured SEO result.
        """

        platform = self._normalize_platform(
            platform
        )

        self._validate_parameters(
            platform=platform,
            title_count=title_count,
            tag_count=tag_count,
            hashtag_count=hashtag_count,
        )

        if content is None:
            content = self._resolve_content()

        if content is None:
            raise RuntimeError(
                "No content was supplied for SEO generation."
            )

        resolved_topic = self._resolve_topic(
            topic
        )

        if provider is None:
            raise RuntimeError(
                "SEO provider was not supplied."
            )

        prompt = self._build_seo_prompt(
            content=content,
            topic=resolved_topic,
            title=title,
            platform=platform,
            language=language,
            audience=audience,
            category=category,
            generate_multiple_titles=(
                generate_multiple_titles
            ),
            title_count=title_count,
            tag_count=tag_count,
            hashtag_count=hashtag_count,
            include_thumbnail_prompt=(
                include_thumbnail_prompt
            ),
            instructions=instructions,
        )

        self.log_info(
            "Generating SEO metadata using provider=%s model=%s",
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
                "SEO provider returned no response."
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
                    "SEO generation failed.",
                )
                if error is not None
                else "SEO generation failed."
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
            "platform": platform,
            "topic": resolved_topic,
            "title": title,
            "language": language,
            "audience": audience,
            "category": category,
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
            "content": content,
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

        # Store complete SEO result.
        self.set_context_value(
            "seo",
            result,
        )

        # Store generated SEO metadata separately.
        self.set_context_value(
            "seo_output",
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
            "SEO metadata generation completed successfully."
        )

        return result

    # ==========================================================================
    # Content Resolution
    # ==========================================================================

    def _resolve_content(
        self,
    ) -> Any | None:
        """
        Resolve the best available content from AgentContext.

        Priority:

        1. final_output
        2. storyboard_output
        3. script_output
        4. script
        """

        context_keys = (
            "final_output",
            "storyboard_output",
            "script_output",
            "script",
        )

        for key in context_keys:
            content = self.get_context_value(
                key
            )

            if content is not None:
                return content

        return None

    # ==========================================================================
    # Topic Resolution
    # ==========================================================================

    def _resolve_topic(
        self,
        topic: str | None,
    ) -> str:
        """
        Resolve the video topic.
        """

        if topic is not None and topic.strip():
            return topic.strip()

        context_topic = self.get_context_value(
            "topic"
        )

        if isinstance(
            context_topic,
            str,
        ) and context_topic.strip():
            return context_topic.strip()

        context_topic = self.get_context_value(
            "script_topic"
        )

        if isinstance(
            context_topic,
            str,
        ) and context_topic.strip():
            return context_topic.strip()

        return ""

    # ==========================================================================
    # Platform
    # ==========================================================================

    @staticmethod
    def _normalize_platform(
        platform: str,
    ) -> str:
        """
        Normalize target platform.
        """

        if not isinstance(
            platform,
            str,
        ):
            raise TypeError(
                "platform must be a string."
            )

        normalized = platform.strip().lower()

        aliases = {
            "yt": "youtube",
            "youtube": "youtube",
        }

        return aliases.get(
            normalized,
            normalized,
        )

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_parameters(
        *,
        platform: str,
        title_count: int,
        tag_count: int,
        hashtag_count: int,
    ) -> None:
        """
        Validate SEO parameters.
        """

        if not platform:
            raise ValueError(
                "platform cannot be empty."
            )

        if title_count <= 0:
            raise ValueError(
                "title_count must be greater than zero."
            )

        if tag_count <= 0:
            raise ValueError(
                "tag_count must be greater than zero."
            )

        if hashtag_count <= 0:
            raise ValueError(
                "hashtag_count must be greater than zero."
            )

    # ==========================================================================
    # Prompt Construction
    # ==========================================================================

    @staticmethod
    def _build_seo_prompt(
        *,
        content: Any,
        topic: str,
        title: str | None,
        platform: str,
        language: str,
        audience: str,
        category: str,
        generate_multiple_titles: bool,
        title_count: int,
        tag_count: int,
        hashtag_count: int,
        include_thumbnail_prompt: bool,
        instructions: str | None,
    ) -> str:
        """
        Build the SEO-generation prompt.
        """

        title_text = (
            title
            if title
            else "No final title has been selected."
        )

        title_instruction = (
            f"Generate {title_count} strong title candidates."
            if generate_multiple_titles
            else "Generate one optimized title."
        )

        thumbnail_instruction = (
            """
THUMBNAIL DIRECTION
-------------------
Provide:

- Main visual subject
- Character/object positioning
- Background
- Lighting
- Emotion
- Composition
- Suggested short thumbnail text
- Image-generation prompt

Keep thumbnail text short and readable.
"""
            if include_thumbnail_prompt
            else ""
        )

        prompt = f"""
You are the YouTube SEO specialist for
Mahy Mythic Labs Studio OS.

Optimize the following video for {platform}.

TOPIC
-----
{topic or "Infer the primary topic from the content."}

CURRENT TITLE
-------------
{title_text}

LANGUAGE
--------
{language}

TARGET AUDIENCE
---------------
{audience}

CATEGORY
--------
{category}

CONTENT
-------
{content}

SEO OBJECTIVES
--------------
{title_instruction}

Generate:

1. Primary recommended title
2. Alternative title candidates
3. SEO-optimized description
4. Short description
5. Primary keywords
6. Long-tail keywords
7. YouTube tags
8. Hashtags
9. Search intent
10. Target audience
11. Suggested category
12. Key topic/entity terms

TITLE RULES
-----------
- Make titles compelling but accurate.
- Do not use misleading clickbait.
- Do not make unsupported claims.
- Avoid unnecessary keyword stuffing.
- Keep titles natural and readable.
- Clearly communicate the actual subject.

DESCRIPTION RULES
-----------------
- Write a natural opening paragraph.
- Explain what viewers will learn.
- Include relevant keywords naturally.
- Do not keyword-stuff.
- Do not make unsupported claims.
- Include appropriate calls to action where useful.

KEYWORD RULES
-------------
- Prioritize relevance over keyword volume.
- Include both broad and long-tail terms.
- Avoid irrelevant trending keywords.

TAG RULES
---------
Generate up to {tag_count} highly relevant tags.

HASHTAG RULES
-------------
Generate approximately {hashtag_count} relevant hashtags.
Do not include irrelevant trending hashtags.

ACCURACY
--------
This channel focuses on mythology, ancient wisdom,
history, science, space, astronomy, and storytelling.

Clearly distinguish mythology, historical claims,
scientific claims, and interpretation where necessary.

Do not fabricate facts simply to improve SEO.

{thumbnail_instruction}

OUTPUT FORMAT
-------------
Return clearly labeled sections:

PRIMARY TITLE
ALTERNATIVE TITLES
DESCRIPTION
SHORT DESCRIPTION
PRIMARY KEYWORDS
LONG-TAIL KEYWORDS
TAGS
HASHTAGS
SEARCH INTENT
TARGET AUDIENCE
CATEGORY
KEY ENTITIES
THUMBNAIL DIRECTION
""".strip()

        if instructions:
            prompt += (
                "\n\nADDITIONAL SEO INSTRUCTIONS\n"
                "--------------------------\n"
                f"{instructions.strip()}"
            )

        return prompt

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