"""
src/models/metadata.py

Shared metadata models used across the Mahy Mythic Labs Studio OS.

This module contains reusable metadata models that can be attached to
Projects, Episodes, Research, Scripts, Assets, and other domain models.

Compatible with:
    - Pydantic v2
    - Python 3.11+
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field, field_validator

from .base import EntityModel, ValueModel


# ==============================================================================
# Enums
# ==============================================================================


class ContentCategory(str, Enum):
    """Primary content categories."""

    HISTORY = "history"
    MYTHOLOGY = "mythology"
    SCIENCE = "science"
    ASTRONOMY = "astronomy"
    PHILOSOPHY = "philosophy"
    OTHER = "other"


class ContentLanguage(str, Enum):
    """Supported content languages."""

    ENGLISH = "en"
    HINDI = "hi"
    ODIA = "or"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"


class ContentStatus(str, Enum):
    """Production lifecycle."""

    DRAFT = "draft"
    RESEARCH = "research"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    GENERATING = "generating"
    REVIEW = "review"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyLevel(str, Enum):
    """Complexity of the topic."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AudienceType(str, Enum):
    """Target audience."""

    GENERAL = "general"
    STUDENTS = "students"
    RESEARCHERS = "researchers"
    CHILDREN = "children"
    PROFESSIONALS = "professionals"


# ==============================================================================
# Supporting Value Objects (immutable, no identity, no touch())
# ==============================================================================


class SourceReference(ValueModel):
    """
    Represents a research reference or citation.
    ValueModel: immutable, compared by value, no identity fields.
    """

    title: str = Field(..., min_length=1)
    author: Optional[str] = None
    url: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[datetime] = None
    notes: Optional[str] = None


class Keyword(ValueModel):
    """
    Search or SEO keyword.
    ValueModel: immutable, compared by value.
    """

    value: str
    weight: float = Field(default=1.0, ge=0.0, le=10.0)


# ==============================================================================
# Cost and Token Usage Value Objects (used by generation.py)
# ==============================================================================


class TokenUsage(ValueModel):
    """Token consumption record for an LLM call."""

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)

    @property
    def has_usage(self) -> bool:
        return self.total_tokens > 0


class CostInfo(ValueModel):
    """Monetary cost record for a generation call."""

    currency: str = "USD"
    input_cost: float = Field(default=0.0, ge=0.0)
    output_cost: float = Field(default=0.0, ge=0.0)

    @property
    def total_cost(self) -> float:
        return round(self.input_cost + self.output_cost, 6)


# ==============================================================================
# Main Metadata Entity (has identity, timestamps, touch())
# ==============================================================================


class Metadata(EntityModel):
    """
    Shared metadata used by all major Studio objects.

    Uses EntityModel because Metadata instances are tracked
    by identity across the production lifecycle.

    Examples
    --------
    - Project
    - Episode
    - Research
    - Script
    - Asset
    """

    # ------------------------------------------------------------------
    # Basic
    # ------------------------------------------------------------------

    title: str = Field(..., min_length=3)

    subtitle: Optional[str] = None

    description: Optional[str] = None

    summary: Optional[str] = None

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    category: ContentCategory = ContentCategory.OTHER

    language: ContentLanguage = ContentLanguage.ENGLISH

    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE

    audience: AudienceType = AudienceType.GENERAL

    status: ContentStatus = ContentStatus.DRAFT

    # ------------------------------------------------------------------
    # SEO
    # ------------------------------------------------------------------

    keywords: List[Keyword] = Field(default_factory=list)

    tags: List[str] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Attribution
    # ------------------------------------------------------------------

    author: str = "Mahy Mythic Labs"

    contributors: List[str] = Field(default_factory=list)

    copyright_holder: str = "Mahy Mythic Labs"

    license: str = "All Rights Reserved"

    # ------------------------------------------------------------------
    # Research
    # ------------------------------------------------------------------

    references: List[SourceReference] = Field(default_factory=list)

    source_count: int = 0

    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    # ------------------------------------------------------------------
    # Production
    # ------------------------------------------------------------------

    estimated_duration_seconds: Optional[int] = Field(
        default=None,
        ge=1,
    )

    estimated_scene_count: Optional[int] = Field(
        default=None,
        ge=1,
    )

    estimated_shot_count: Optional[int] = Field(
        default=None,
        ge=1,
    )

    # ------------------------------------------------------------------
    # Custom
    # ------------------------------------------------------------------

    custom: Dict[str, str] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: List[str]) -> List[str]:
        """Remove duplicates and normalize."""
        normalized = {
            tag.strip().lower()
            for tag in value
            if tag.strip()
        }
        return sorted(normalized)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError(
                "Title must contain at least 3 characters."
            )
        return value

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def add_tag(self, tag: str) -> None:
        """Add a tag if it does not already exist."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def add_reference(self, reference: SourceReference) -> None:
        """Add a research reference."""
        self.references.append(reference)
        self.source_count = len(self.references)
        self.touch()

    def add_keyword(self, keyword: Keyword) -> None:
        """Add SEO keyword."""
        self.keywords.append(keyword)
        self.touch()

    def publish(self) -> None:
        """Mark object as published."""
        self.status = ContentStatus.PUBLISHED
        self.touch()

    def archive(self) -> None:
        """Archive object."""
        self.status = ContentStatus.ARCHIVED
        self.touch()

    def reset(self) -> None:
        """Reset production status."""
        self.status = ContentStatus.DRAFT
        self.touch()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_published(self) -> bool:
        return self.status == ContentStatus.PUBLISHED

    @property
    def last_modified(self) -> datetime:
        return self.updated_at

    @property
    def age(self) -> float:
        """Age of this metadata object in seconds."""
        return (datetime.now(UTC) - self.created_at).total_seconds()
