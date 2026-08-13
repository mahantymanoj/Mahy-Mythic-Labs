"""
src/agents/quality_agent.py

Quality assurance agent for Mahy Mythic Labs Studio OS.

Responsibilities
----------------
- Validate research output
- Validate script quality
- Validate storyboard quality
- Validate generated assets
- Detect missing or potentially problematic content
- Produce structured quality reports
- Store quality results in AgentContext
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
# Quality Agent
# ==============================================================================


class QualityAgent(BaseAgent):
    """
    Agent responsible for quality assurance across the production pipeline.

    QualityAgent can validate one or more production stages:

        research
        script
        storyboard
        image
        video
        narration
        final

    The agent can perform deterministic checks locally and can
    optionally use an LLM provider for deeper semantic review.
    """

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            agent_type=AgentType.QUALITY,
            name="quality_agent",
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
        Initialize the QualityAgent.
        """

        initialized = await super().initialize(
            context=context
        )

        if not initialized:
            return False

        logger.info(
            "QualityAgent initialized"
        )

        return True

    # ==========================================================================
    # Execution
    # ==========================================================================

    async def execute(
        self,
        content: Any | None = None,
        *,
        stage: str = "final",
        provider: Any | None = None,
        model: str | None = None,
        minimum_score: float = 70.0,
        use_llm_review: bool = False,
        instructions: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Perform quality validation.

        Parameters
        ----------
        content:
            Content to validate.

            If omitted, content is resolved from AgentContext
            according to the requested stage.

        stage:
            Pipeline stage being reviewed.

        provider:
            Optional LLM provider for semantic review.

        model:
            Optional LLM model.

        minimum_score:
            Minimum passing score from 0 to 100.

        use_llm_review:
            Whether to perform an additional LLM-based review.

        instructions:
            Additional QA instructions.

        kwargs:
            Additional provider-specific parameters.

        Returns
        -------
        dict[str, Any]
            Structured quality report.
        """

        stage = self._normalize_stage(stage)

        self._validate_parameters(
            stage=stage,
            minimum_score=minimum_score,
        )

        if content is None:
            content = self._resolve_content(
                stage
            )

        self._validate_content(
            content
        )

        self.log_info(
            "Starting quality review for stage=%s",
            stage,
        )

        # ----------------------------------------------------------------------
        # Deterministic checks
        # ----------------------------------------------------------------------

        checks = self._run_deterministic_checks(
            content=content,
            stage=stage,
        )

        deterministic_score = self._calculate_score(
            checks
        )

        llm_review: dict[str, Any] | None = None

        # ----------------------------------------------------------------------
        # Optional semantic LLM review
        # ----------------------------------------------------------------------

        if use_llm_review:
            if provider is None:
                raise RuntimeError(
                    "LLM review was requested, but no "
                    "quality-review provider was supplied."
                )

            review_prompt = self._build_review_prompt(
                content=content,
                stage=stage,
                instructions=instructions,
            )

            self.log_info(
                "Running semantic quality review using provider=%s",
                self._provider_name(provider),
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
                review_prompt,
                **provider_kwargs,
            )

            if response is None:
                raise RuntimeError(
                    "Quality-review provider returned no response."
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
                        "Semantic quality review failed.",
                    )
                    if error is not None
                    else "Semantic quality review failed."
                )

                raise RuntimeError(
                    error_message
                )

            llm_review = {
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
                "output": getattr(
                    response,
                    "output",
                    None,
                ),
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

        # ----------------------------------------------------------------------
        # Final score
        # ----------------------------------------------------------------------

        final_score = deterministic_score

        passed = (
            final_score >= minimum_score
            and self._has_no_blocking_failures(
                checks
            )
        )

        result = {
            "stage": stage,
            "passed": passed,
            "score": final_score,
            "minimum_score": minimum_score,
            "checks": checks,
            "llm_review": llm_review,
            "blocking_failures": [
                check["name"]
                for check in checks
                if check["blocking"]
                and not check["passed"]
            ],
            "recommendations": self._build_recommendations(
                checks
            ),
        }

        # Store QA information for downstream workflow logic.
        self.set_context_value(
            "quality_report",
            result,
        )

        self.set_context_value(
            f"quality_{stage}",
            result,
        )

        self.set_metadata(
            "last_quality_stage",
            stage,
        )

        self.set_metadata(
            "last_quality_score",
            final_score,
        )

        self.log_info(
            "Quality review completed: stage=%s score=%.1f passed=%s",
            stage,
            final_score,
            passed,
        )

        return result

    # ==========================================================================
    # Content Resolution
    # ==========================================================================

    def _resolve_content(
        self,
        stage: str,
    ) -> Any:
        """
        Resolve content from AgentContext based on pipeline stage.
        """

        mapping = {
            "research": "research_output",
            "script": "script_output",
            "storyboard": "storyboard_output",
            "image": "image_generation",
            "video": "video_generation",
            "narration": "narration_generation",
            "final": "final_output",
        }

        key = mapping.get(stage)

        if key:
            content = self.get_context_value(
                key
            )

            if content is not None:
                return content

        # Try generic content.
        content = self.get_context_value(
            "content"
        )

        if content is not None:
            return content

        raise RuntimeError(
            f"No content found for quality stage '{stage}'."
        )

    # ==========================================================================
    # Stage Normalization
    # ==========================================================================

    @staticmethod
    def _normalize_stage(
        stage: str,
    ) -> str:
        """
        Normalize and validate the requested quality stage.
        """

        if not isinstance(
            stage,
            str,
        ):
            raise TypeError(
                "stage must be a string."
            )

        normalized = stage.strip().lower()

        aliases = {
            "research": "research",
            "script": "script",
            "story": "script",
            "storyboard": "storyboard",
            "image": "image",
            "images": "image",
            "video": "video",
            "videos": "video",
            "narration": "narration",
            "audio": "narration",
            "final": "final",
        }

        if normalized not in aliases:
            raise ValueError(
                f"Unsupported quality stage: {stage!r}"
            )

        return aliases[normalized]

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_parameters(
        *,
        stage: str,
        minimum_score: float,
    ) -> None:
        """
        Validate quality-agent parameters.
        """

        if not stage.strip():
            raise ValueError(
                "stage cannot be empty."
            )

        if not 0 <= minimum_score <= 100:
            raise ValueError(
                "minimum_score must be between 0 and 100."
            )

    @staticmethod
    def _validate_content(
        content: Any,
    ) -> None:
        """
        Validate that content exists.
        """

        if content is None:
            raise ValueError(
                "Content cannot be None."
            )

        if isinstance(
            content,
            str,
        ) and not content.strip():
            raise ValueError(
                "Content cannot be an empty string."
            )

    # ==========================================================================
    # Deterministic Quality Checks
    # ==========================================================================

    def _run_deterministic_checks(
        self,
        *,
        content: Any,
        stage: str,
    ) -> list[dict[str, Any]]:
        """
        Run deterministic checks appropriate for the stage.
        """

        checks: list[dict[str, Any]] = []

        checks.append(
            self._check_content_exists(
                content
            )
        )

        checks.append(
            self._check_content_structure(
                content
            )
        )

        if stage in {
            "research",
            "script",
            "storyboard",
            "final",
        }:
            checks.append(
                self._check_text_length(
                    content
                )
            )

        if stage == "script":
            checks.extend(
                self._check_script_quality(
                    content
                )
            )

        elif stage == "storyboard":
            checks.extend(
                self._check_storyboard_quality(
                    content
                )
            )

        elif stage in {
            "image",
            "video",
            "narration",
        }:
            checks.extend(
                self._check_asset_quality(
                    content,
                    stage,
                )
            )

        return checks

    # ==========================================================================
    # Generic Checks
    # ==========================================================================

    @staticmethod
    def _check_content_exists(
        content: Any,
    ) -> dict[str, Any]:
        """
        Verify that content exists.
        """

        passed = content is not None

        return {
            "name": "content_exists",
            "passed": passed,
            "blocking": True,
            "message": (
                "Content exists."
                if passed
                else "Content is missing."
            ),
        }

    @staticmethod
    def _check_content_structure(
        content: Any,
    ) -> dict[str, Any]:
        """
        Verify that content has a usable structure.
        """

        valid_types = (
            str,
            dict,
            list,
            tuple,
        )

        passed = isinstance(
            content,
            valid_types,
        )

        return {
            "name": "content_structure",
            "passed": passed,
            "blocking": True,
            "message": (
                "Content has a supported structure."
                if passed
                else "Content has an unsupported structure."
            ),
        }

    @staticmethod
    def _check_text_length(
        content: Any,
    ) -> dict[str, Any]:
        """
        Perform a basic text-length sanity check.
        """

        if isinstance(
            content,
            str,
        ):
            length = len(
                content.strip()
            )
        elif isinstance(
            content,
            dict,
        ):
            text_parts = []

            for value in content.values():
                if isinstance(
                    value,
                    str,
                ):
                    text_parts.append(value)

            length = len(
                " ".join(text_parts).strip()
            )
        else:
            length = 1

        passed = length > 20

        return {
            "name": "content_length",
            "passed": passed,
            "blocking": False,
            "message": (
                "Content contains sufficient text."
                if passed
                else "Content appears unusually short."
            ),
            "length": length,
        }

    # ==========================================================================
    # Script Checks
    # ==========================================================================

    @staticmethod
    def _check_script_quality(
        content: Any,
    ) -> list[dict[str, Any]]:
        """
        Run basic checks against generated scripts.
        """

        checks: list[dict[str, Any]] = []

        text = QualityAgent._extract_text(
            content
        ).lower()

        checks.append(
            {
                "name": "script_has_content",
                "passed": len(text) > 50,
                "blocking": True,
                "message": (
                    "Script contains sufficient content."
                    if len(text) > 50
                    else "Script is too short."
                ),
            }
        )

        checks.append(
            {
                "name": "script_has_hook",
                "passed": QualityAgent._contains_any(
                    text,
                    (
                        "hook",
                        "introduction",
                        "opening",
                    ),
                ),
                "blocking": False,
                "message": (
                    "Potential opening/hook detected."
                    if QualityAgent._contains_any(
                        text,
                        (
                            "hook",
                            "introduction",
                            "opening",
                        ),
                    )
                    else "No explicit hook/opening marker detected."
                ),
            }
        )

        checks.append(
            {
                "name": "script_has_conclusion",
                "passed": QualityAgent._contains_any(
                    text,
                    (
                        "conclusion",
                        "ending",
                        "final",
                    ),
                ),
                "blocking": False,
                "message": (
                    "Potential conclusion detected."
                    if QualityAgent._contains_any(
                        text,
                        (
                            "conclusion",
                            "ending",
                            "final",
                        ),
                    )
                    else "No explicit conclusion marker detected."
                ),
            }
        )

        return checks

    # ==========================================================================
    # Storyboard Checks
    # ==========================================================================

    @staticmethod
    def _check_storyboard_quality(
        content: Any,
    ) -> list[dict[str, Any]]:
        """
        Run basic storyboard checks.
        """

        checks: list[dict[str, Any]] = []

        text = QualityAgent._extract_text(
            content
        ).lower()

        checks.append(
            {
                "name": "storyboard_has_scenes",
                "passed": QualityAgent._contains_any(
                    text,
                    (
                        "scene",
                        "shot",
                    ),
                ),
                "blocking": True,
                "message": (
                    "Scene/shot structure detected."
                    if QualityAgent._contains_any(
                        text,
                        (
                            "scene",
                            "shot",
                        ),
                    )
                    else "No scene or shot structure detected."
                ),
            }
        )

        checks.append(
            {
                "name": "storyboard_has_visual_direction",
                "passed": QualityAgent._contains_any(
                    text,
                    (
                        "visual",
                        "camera",
                        "lighting",
                        "environment",
                    ),
                ),
                "blocking": False,
                "message": (
                    "Visual production direction detected."
                    if QualityAgent._contains_any(
                        text,
                        (
                            "visual",
                            "camera",
                            "lighting",
                            "environment",
                        ),
                    )
                    else "Limited visual production direction detected."
                ),
            }
        )

        return checks

    # ==========================================================================
    # Asset Checks
    # ==========================================================================

    @staticmethod
    def _check_asset_quality(
        content: Any,
        stage: str,
    ) -> list[dict[str, Any]]:
        """
        Run basic checks against generated assets.
        """

        checks: list[dict[str, Any]] = []

        if isinstance(
            content,
            dict,
        ):
            output = content.get(
                "output"
            )

            checks.append(
                {
                    "name": f"{stage}_output_exists",
                    "passed": output is not None,
                    "blocking": True,
                    "message": (
                        f"{stage.title()} output exists."
                        if output is not None
                        else f"{stage.title()} output is missing."
                    ),
                }
            )

            provider = content.get(
                "provider"
            )

            checks.append(
                {
                    "name": f"{stage}_provider_recorded",
                    "passed": bool(provider),
                    "blocking": False,
                    "message": (
                        "Generation provider is recorded."
                        if provider
                        else "Generation provider is not recorded."
                    ),
                }
            )

        else:
            checks.append(
                {
                    "name": f"{stage}_asset_present",
                    "passed": bool(content),
                    "blocking": True,
                    "message": (
                        f"{stage.title()} asset is present."
                        if content
                        else f"{stage.title()} asset is missing."
                    ),
                }
            )

        return checks

    # ==========================================================================
    # Score Calculation
    # ==========================================================================

    @staticmethod
    def _calculate_score(
        checks: list[dict[str, Any]],
    ) -> float:
        """
        Calculate a quality score from 0 to 100.
        """

        if not checks:
            return 0.0

        passed = sum(
            1
            for check in checks
            if check.get("passed")
        )

        return round(
            (passed / len(checks)) * 100,
            2,
        )

    @staticmethod
    def _has_no_blocking_failures(
        checks: list[dict[str, Any]],
    ) -> bool:
        """
        Return True when no blocking check failed.
        """

        return not any(
            check.get("blocking")
            and not check.get("passed")
            for check in checks
        )

    # ==========================================================================
    # Recommendations
    # ==========================================================================

    @staticmethod
    def _build_recommendations(
        checks: list[dict[str, Any]],
    ) -> list[str]:
        """
        Build recommendations from failed checks.
        """

        recommendations: list[str] = []

        for check in checks:
            if check.get("passed"):
                continue

            name = check.get(
                "name",
                "unknown",
            )

            if name == "content_exists":
                recommendations.append(
                    "Generate or provide the missing content."
                )

            elif name == "content_structure":
                recommendations.append(
                    "Convert the content into a supported structured format."
                )

            elif name == "content_length":
                recommendations.append(
                    "Review the content because it appears unusually short."
                )

            elif name == "script_has_content":
                recommendations.append(
                    "Expand the script before continuing to production."
                )

            elif name == "script_has_hook":
                recommendations.append(
                    "Strengthen the opening hook."
                )

            elif name == "script_has_conclusion":
                recommendations.append(
                    "Add or strengthen the conclusion."
                )

            elif name == "storyboard_has_scenes":
                recommendations.append(
                    "Break the script into explicit scenes and shots."
                )

            elif name == "storyboard_has_visual_direction":
                recommendations.append(
                    "Add camera, lighting, environment, and visual direction."
                )

            elif name.endswith(
                "_output_exists"
            ):
                recommendations.append(
                    "Verify that the generated asset was returned correctly."
                )

            elif name.endswith(
                "_provider_recorded"
            ):
                recommendations.append(
                    "Record the provider used for the generated asset."
                )

            elif name.endswith(
                "_asset_present"
            ):
                recommendations.append(
                    "Verify that the generated asset exists."
                )

        return recommendations

    # ==========================================================================
    # LLM Review Prompt
    # ==========================================================================

    @staticmethod
    def _build_review_prompt(
        *,
        content: Any,
        stage: str,
        instructions: str | None,
    ) -> str:
        """
        Build an LLM-based semantic quality-review prompt.
        """

        prompt = f"""
You are the quality-control specialist for
Mahy Mythic Labs Studio OS.

Review the following {stage} production output.

CONTENT
-------
{content}

Evaluate:

1. Factual consistency
2. Internal consistency
3. Narrative quality
4. Clarity
5. Production readiness
6. Mythology/history distinction
7. Scientific accuracy where applicable
8. Visual consistency where applicable
9. Unsupported claims
10. Potential hallucinations
11. Missing information
12. Problems that downstream production agents may encounter

Return:

- Overall assessment
- Critical issues
- Major issues
- Minor issues
- Recommended fixes
- Production readiness assessment

Do not rewrite the entire content.
Focus on identifying problems and actionable improvements.
""".strip()

        if instructions:
            prompt += (
                "\n\nADDITIONAL QA INSTRUCTIONS\n"
                "-------------------------\n"
                f"{instructions.strip()}"
            )

        return prompt

    # ==========================================================================
    # Text Helpers
    # ==========================================================================

    @staticmethod
    def _extract_text(
        content: Any,
    ) -> str:
        """
        Convert common content structures into text for checks.
        """

        if isinstance(
            content,
            str,
        ):
            return content

        if isinstance(
            content,
            dict,
        ):
            parts: list[str] = []

            for key, value in content.items():
                parts.append(
                    str(key)
                )

                if isinstance(
                    value,
                    (str, int, float),
                ):
                    parts.append(
                        str(value)
                    )

            return " ".join(parts)

        if isinstance(
            content,
            (list, tuple),
        ):
            return " ".join(
                str(item)
                for item in content
            )

        return str(content)

    @staticmethod
    def _contains_any(
        text: str,
        values: tuple[str, ...],
    ) -> bool:
        """
        Return True when any target value exists in text.
        """

        return any(
            value in text
            for value in values
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