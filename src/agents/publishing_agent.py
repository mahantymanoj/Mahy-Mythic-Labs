"""
src/agents/publishing_agent.py

Publishing preparation agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Validate final production outputs
- Collect SEO metadata
- Prepare YouTube publishing metadata
- Prepare upload/package information
- Validate required publishing fields
- Generate publishing checklist
- Store publishing package in AgentContext

Important
---------
This agent does NOT automatically upload or publish content
to YouTube.

Actual publishing should be handled by a future publishing
integration/service after explicit user approval.

Python
------
>= 3.11
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .base_agent import (
    AgentContext,
    AgentType,
    BaseAgent,
)


logger = logging.getLogger(__name__)


# ==============================================================================
# Publishing Agent
# ==============================================================================


class PublishingAgent(BaseAgent):
    """
    Prepare a production package for publishing.

    PublishingAgent sits near the end of the Studio OS pipeline.

    Typical flow:

        ResearchAgent
              |
        ScriptAgent
              |
        StoryboardAgent
              |
        ImageAgent / VideoAgent
              |
        NarrationAgent
              |
        QualityAgent
              |
        SEOAgent
              |
        PublishingAgent
              |
        Final Publishing Package

    This class intentionally does NOT upload to YouTube.
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.PUBLISHING,
            name="publishing_agent",
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
        Initialize the PublishingAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "PublishingAgent initialized"
        )

        return True

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def execute(
        self,
        *,
        video_path: str | Path | None = None,
        thumbnail_path: str | Path | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        hashtags: list[str] | None = None,
        category: str = "Education",
        visibility: str = "private",
        scheduled_at: str | None = None,
        content: Any | None = None,
        seo: Any | None = None,
        quality_report: Any | None = None,
        platform: str = "youtube",
        allow_publish: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Prepare a publishing package.

        Parameters
        ----------
        video_path:
            Path to the final rendered video.

        thumbnail_path:
            Path to the thumbnail image.

        title:
            YouTube title.

        description:
            YouTube description.

        tags:
            YouTube tags.

        hashtags:
            YouTube hashtags.

        category:
            Target YouTube category.

        visibility:
            Intended visibility:
            private, unlisted, or public.

        scheduled_at:
            Optional future publishing timestamp.

        content:
            Optional final content.

        seo:
            SEO output. If omitted, resolved from AgentContext.

        quality_report:
            Quality report. If omitted, resolved from AgentContext.

        platform:
            Target publishing platform.

        allow_publish:
            Safety flag.

            This agent still does not upload automatically.
            The flag only records whether publishing was
            explicitly authorized for a future publishing
            integration.

        kwargs:
            Additional publishing metadata.

        Returns
        -------
        dict[str, Any]
            Publishing package and validation result.
        """

        platform = self._normalize_platform(
            platform
        )

        visibility = self._normalize_visibility(
            visibility
        )

        # ----------------------------------------------------------------------
        # Resolve context values
        # ----------------------------------------------------------------------

        seo = (
            seo
            if seo is not None
            else self._resolve_seo()
        )

        quality_report = (
            quality_report
            if quality_report is not None
            else self._resolve_quality_report()
        )

        content = (
            content
            if content is not None
            else self._resolve_content()
        )

        # ----------------------------------------------------------------------
        # Resolve SEO metadata
        # ----------------------------------------------------------------------

        seo_data = self._extract_seo_data(
            seo
        )

        if title is None:
            title = self._extract_string(
                seo_data,
                "primary_title",
            )

        if description is None:
            description = self._extract_string(
                seo_data,
                "description",
            )

        if not tags:
            tags = self._extract_list(
                seo_data,
                "tags",
            )

        if not hashtags:
            hashtags = self._extract_list(
                seo_data,
                "hashtags",
            )

        # ----------------------------------------------------------------------
        # Resolve thumbnail
        # ----------------------------------------------------------------------

        if thumbnail_path is None:
            thumbnail_path = self._resolve_thumbnail_path(
                seo_data
            )

        # ----------------------------------------------------------------------
        # Validate package
        # ----------------------------------------------------------------------

        validation = self._validate_publish_package(
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=title,
            description=description,
            quality_report=quality_report,
            visibility=visibility,
        )

        ready_to_publish = validation["ready"]

        # ----------------------------------------------------------------------
        # Build publishing package
        # ----------------------------------------------------------------------

        package = {
            "platform": platform,
            "video": {
                "path": (
                    str(video_path)
                    if video_path is not None
                    else None
                ),
            },
            "thumbnail": {
                "path": (
                    str(thumbnail_path)
                    if thumbnail_path is not None
                    else None
                ),
            },
            "metadata": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "hashtags": hashtags or [],
                "category": category,
                "visibility": visibility,
                "scheduled_at": scheduled_at,
            },
            "content": content,
            "seo": seo,
            "quality_report": quality_report,
            "validation": validation,
            "publishing": {
                "requested": bool(
                    allow_publish
                ),
                "executed": False,
                "status": (
                    "ready"
                    if ready_to_publish
                    else "blocked"
                ),
                "automatic_upload": False,
            },
            "extra": kwargs,
        }

        # ----------------------------------------------------------------------
        # Store in AgentContext
        # ----------------------------------------------------------------------

        self.set_context_value(
            "publishing_package",
            package,
        )

        self.set_context_value(
            "publish_ready",
            ready_to_publish,
        )

        self.set_metadata(
            "publishing_status",
            package["publishing"]["status"],
        )

        self.log_info(
            "Publishing package prepared: ready=%s",
            ready_to_publish,
        )

        return package

    # ==========================================================================
    # SEO Resolution
    # ==========================================================================

    def _resolve_seo(
        self,
    ) -> Any | None:
        """
        Resolve SEO output from AgentContext.
        """

        seo = self.get_context_value(
            "seo_output"
        )

        if seo is not None:
            return seo

        seo = self.get_context_value(
            "seo"
        )

        return seo

    # ==========================================================================
    # Quality Resolution
    # ==========================================================================

    def _resolve_quality_report(
        self,
    ) -> Any | None:
        """
        Resolve QualityAgent output from AgentContext.
        """

        return self.get_context_value(
            "quality_report"
        )

    # ==========================================================================
    # Content Resolution
    # ==========================================================================

    def _resolve_content(
        self,
    ) -> Any | None:
        """
        Resolve final content from AgentContext.
        """

        for key in (
            "final_output",
            "video_output",
            "storyboard_output",
            "script_output",
        ):
            value = self.get_context_value(
                key
            )

            if value is not None:
                return value

        return None

    # ==========================================================================
    # SEO Data Extraction
    # ==========================================================================

    @staticmethod
    def _extract_seo_data(
        seo: Any,
    ) -> dict[str, Any]:
        """
        Extract structured SEO data.

        SEOAgent may return either a structured dictionary
        or raw LLM text.

        Raw text is preserved under 'raw_output'.
        """

        if seo is None:
            return {}

        if isinstance(
            seo,
            dict,
        ):
            output = seo.get(
                "output"
            )

            if isinstance(
                output,
                dict,
            ):
                return {
                    **seo,
                    **output,
                }

            return seo

        return {
            "raw_output": seo
        }

    # ==========================================================================
    # Value Extraction
    # ==========================================================================

    @staticmethod
    def _extract_string(
        data: dict[str, Any],
        key: str,
    ) -> str | None:
        """
        Extract a string value from a dictionary.
        """

        value = data.get(
            key
        )

        if isinstance(
            value,
            str,
        ):
            value = value.strip()

            if value:
                return value

        return None

    @staticmethod
    def _extract_list(
        data: dict[str, Any],
        key: str,
    ) -> list[str]:
        """
        Extract a list of strings from a dictionary.
        """

        value = data.get(
            key
        )

        if isinstance(
            value,
            list,
        ):
            return [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

        if isinstance(
            value,
            tuple,
        ):
            return [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

        if isinstance(
            value,
            str,
        ):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return []

    # ==========================================================================
    # Thumbnail Resolution
    # ==========================================================================

    @staticmethod
    def _resolve_thumbnail_path(
        seo_data: dict[str, Any],
    ) -> str | None:
        """
        Attempt to resolve a thumbnail path from SEO data.
        """

        for key in (
            "thumbnail_path",
            "thumbnail",
            "thumbnail_file",
        ):
            value = seo_data.get(
                key
            )

            if isinstance(
                value,
                str,
            ) and value.strip():
                return value.strip()

        return None

    # ==========================================================================
    # Package Validation
    # ==========================================================================

    @staticmethod
    def _validate_publish_package(
        *,
        video_path: str | Path | None,
        thumbnail_path: str | Path | None,
        title: str | None,
        description: str | None,
        quality_report: Any | None,
        visibility: str,
    ) -> dict[str, Any]:
        """
        Validate the publishing package.

        The method intentionally does not require a thumbnail
        because thumbnail generation may be optional.
        """

        errors: list[str] = []
        warnings: list[str] = []

        # ----------------------------------------------------------------------
        # Video
        # ----------------------------------------------------------------------

        if video_path is None:
            errors.append(
                "Final video path is missing."
            )
        else:
            video = Path(
                video_path
            )

            if not video.exists():
                errors.append(
                    f"Video file does not exist: {video}"
                )

            elif not video.is_file():
                errors.append(
                    f"Video path is not a file: {video}"
                )

        # ----------------------------------------------------------------------
        # Title
        # ----------------------------------------------------------------------

        if not title:
            errors.append(
                "Video title is missing."
            )

        elif not title.strip():
            errors.append(
                "Video title is empty."
            )

        # ----------------------------------------------------------------------
        # Description
        # ----------------------------------------------------------------------

        if not description:
            warnings.append(
                "Video description is missing."
            )

        # ----------------------------------------------------------------------
        # Thumbnail
        # ----------------------------------------------------------------------

        if thumbnail_path is None:
            warnings.append(
                "Thumbnail path is not provided."
            )
        else:
            thumbnail = Path(
                thumbnail_path
            )

            if not thumbnail.exists():
                warnings.append(
                    f"Thumbnail file does not exist: {thumbnail}"
                )

            elif not thumbnail.is_file():
                warnings.append(
                    f"Thumbnail path is not a file: {thumbnail}"
                )

        # ----------------------------------------------------------------------
        # Quality
        # ----------------------------------------------------------------------

        quality_passed = True

        if isinstance(
            quality_report,
            dict,
        ):
            quality_passed = bool(
                quality_report.get(
                    "passed",
                    True,
                )
            )

            if not quality_passed:
                errors.append(
                    "QualityAgent has not approved the content."
                )

        elif quality_report is None:
            warnings.append(
                "No quality report was provided."
            )

        # ----------------------------------------------------------------------
        # Visibility
        # ----------------------------------------------------------------------

        if visibility not in {
            "private",
            "unlisted",
            "public",
        }:
            errors.append(
                f"Unsupported visibility: {visibility}"
            )

        return {
            "ready": not errors,
            "errors": errors,
            "warnings": warnings,
            "quality_passed": quality_passed,
        }

    # ==========================================================================
    # Platform
    # ==========================================================================

    @staticmethod
    def _normalize_platform(
        platform: str,
    ) -> str:
        """
        Normalize publishing platform.
        """

        if not isinstance(
            platform,
            str,
        ):
            raise TypeError(
                "platform must be a string."
            )

        normalized = platform.strip().lower()

        if normalized in {
            "yt",
            "youtube",
        }:
            return "youtube"

        return normalized

    # ==========================================================================
    # Visibility
    # ==========================================================================

    @staticmethod
    def _normalize_visibility(
        visibility: str,
    ) -> str:
        """
        Normalize YouTube visibility.
        """

        if not isinstance(
            visibility,
            str,
        ):
            raise TypeError(
                "visibility must be a string."
            )

        normalized = visibility.strip().lower()

        aliases = {
            "private": "private",
            "unlisted": "unlisted",
            "public": "public",
        }

        if normalized not in aliases:
            raise ValueError(
                "visibility must be one of: "
                "private, unlisted, public."
            )

        return aliases[normalized]