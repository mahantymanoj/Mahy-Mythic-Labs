"""
src/models/research.py

Research domain models.

Research is the factual foundation for an Episode.

It stores references, notes, findings, citations,
summaries, and verified facts that are later used
to generate scripts and storyboards.

Hierarchy
---------
Project
    └── Episode
            └── Research
                    ├── ResearchSource
                    └── ResearchFinding

Python
------
>=3.11

Pydantic
---------
>=2.x
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import Field, HttpUrl, field_validator

from .base import EntityModel, ValueModel

# ==============================================================================
# Enums
# ==============================================================================


class ResearchStatus(str, Enum):
    """
    Research lifecycle.
    """

    DRAFT = "draft"

    COLLECTING = "collecting"

    REVIEW = "review"

    VERIFIED = "verified"

    APPROVED = "approved"

    ARCHIVED = "archived"


class SourceType(str, Enum):
    """
    Research source type.
    """

    BOOK = "book"

    WEBSITE = "website"

    PAPER = "paper"

    VIDEO = "video"

    PODCAST = "podcast"

    DOCUMENTARY = "documentary"

    INTERVIEW = "interview"

    PERSONAL_NOTE = "personal_note"

    OTHER = "other"

# ==============================================================================
# Research Source
# ==============================================================================


class ResearchSource(ValueModel):
    """
    External source used during research.
    """

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    source_type: SourceType

    author: str | None = None

    publisher: str | None = None

    url: HttpUrl | None = None

    publication_year: int | None = Field(
        default=None,
        ge=1,
    )

    credibility_score: float = Field(
        default=5.0,
        ge=0,
        le=10,
    )

    verified: bool = False

    notes: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("title")
    @classmethod
    def validate_title(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Source title cannot be empty."
            )

        return value

# ==============================================================================
# Research Finding
# ==============================================================================


class ResearchFinding(ValueModel):
    """
    Verified research fact or observation.
    """

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str

    source_index: int | None = Field(
        default=None,
        ge=0,
        description="Index into Research.sources.",
    )

    confidence_score: float = Field(
        default=5.0,
        ge=0,
        le=10,
    )

    verified: bool = False

    tags: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("title")
    @classmethod
    def validate_title(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Finding title cannot be empty."
            )

        return value

# ==============================================================================
# Research Entity
# ==============================================================================


class Research(EntityModel):
    """
    Research document for an episode.

    Research is the factual foundation used to create
    scripts, storyboards, scenes and AI prompts.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    project_id: UUID = Field(
        description="Associated project."
    )

    episode_id: UUID = Field(
        description="Associated episode."
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    topic: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status: ResearchStatus = Field(
        default=ResearchStatus.DRAFT,
    )

    approved: bool = False

    verified: bool = False

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    summary: str | None = None

    objective: str | None = None

    findings: list[ResearchFinding] = Field(
        default_factory=list,
    )

    sources: list[ResearchSource] = Field(
        default_factory=list,
    )

    assumptions: list[str] = Field(
        default_factory=list,
    )

    keywords: list[str] = Field(
        default_factory=list,
    )

    notes: str | None = None

    # ------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------

    confidence_score: float = Field(
        default=5.0,
        ge=0,
        le=10,
    )

    completeness_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    tags: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("title")
    @classmethod
    def validate_title(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Title cannot be empty."
            )

        return value

    @field_validator("topic")
    @classmethod
    def validate_topic(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Topic cannot be empty."
            )

        return value

    # ------------------------------------------------------------------
    # Source Management
    # ------------------------------------------------------------------

    def add_source(
        self,
        source: ResearchSource,
    ) -> None:
        """
        Add a research source.
        """

        self.sources.append(source)
        self.touch()

    def remove_source(
        self,
        index: int,
    ) -> None:
        """
        Remove a research source.
        """

        if 0 <= index < len(self.sources):
            self.sources.pop(index)
            self.touch()

    # ------------------------------------------------------------------
    # Finding Management
    # ------------------------------------------------------------------

    def add_finding(
        self,
        finding: ResearchFinding,
    ) -> None:
        """
        Add a research finding.
        """

        self.findings.append(finding)
        self.touch()

    def remove_finding(
        self,
        index: int,
    ) -> None:
        """
        Remove a research finding.
        """

        if 0 <= index < len(self.findings):
            self.findings.pop(index)
            self.touch()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_collection(self) -> None:
        """
        Begin research collection.
        """

        self.status = ResearchStatus.COLLECTING
        self.touch()

    def submit_for_review(self) -> None:
        """
        Submit research for review.
        """

        self.status = ResearchStatus.REVIEW
        self.touch()

    def verify(self) -> None:
        """
        Mark research as verified.
        """

        self.status = ResearchStatus.VERIFIED
        self.verified = True
        self.touch()

    def approve(self) -> None:
        """
        Approve research.
        """

        self.status = ResearchStatus.APPROVED
        self.approved = True
        self.touch()

    def archive(self) -> None:
        """
        Archive research.
        """

        self.status = ResearchStatus.ARCHIVED
        self.touch()

    # ------------------------------------------------------------------
    # Keyword Management
    # ------------------------------------------------------------------

    def add_keyword(
        self,
        keyword: str,
    ) -> None:
        """
        Add a keyword.
        """

        keyword = keyword.strip()

        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.touch()

    def remove_keyword(
        self,
        keyword: str,
    ) -> None:
        """
        Remove a keyword.
        """

        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.touch()

    # ------------------------------------------------------------------
    # Assumption Management
    # ------------------------------------------------------------------

    def add_assumption(
        self,
        assumption: str,
    ) -> None:
        """
        Add an assumption.
        """

        assumption = assumption.strip()

        if assumption:
            self.assumptions.append(assumption)
            self.touch()

    def remove_assumption(
        self,
        index: int,
    ) -> None:
        """
        Remove an assumption.
        """

        if 0 <= index < len(self.assumptions):
            self.assumptions.pop(index)
            self.touch()

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def source_count(self) -> int:
        """
        Total research sources.
        """
        return len(self.sources)

    @property
    def finding_count(self) -> int:
        """
        Total research findings.
        """
        return len(self.findings)

    @property
    def verified_source_count(self) -> int:
        """
        Number of verified sources.
        """
        return sum(
            source.verified
            for source in self.sources
        )

    @property
    def verified_finding_count(self) -> int:
        """
        Number of verified findings.
        """
        return sum(
            finding.verified
            for finding in self.findings
        )

    @property
    def verification_percentage(self) -> float:
        """
        Percentage of verified findings.
        """

        if not self.findings:
            return 0.0

        return round(
            self.verified_finding_count
            / len(self.findings)
            * 100,
            2,
        )

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def is_draft(self) -> bool:
        return self.status == ResearchStatus.DRAFT

    @property
    def is_collecting(self) -> bool:
        return self.status == ResearchStatus.COLLECTING

    @property
    def is_review(self) -> bool:
        return self.status == ResearchStatus.REVIEW

    @property
    def is_verified(self) -> bool:
        return self.status == ResearchStatus.VERIFIED

    @property
    def is_approved(self) -> bool:
        return self.status == ResearchStatus.APPROVED

    @property
    def is_archived(self) -> bool:
        return self.status == ResearchStatus.ARCHIVED

    @property
    def has_sources(self) -> bool:
        return bool(self.sources)

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    # ------------------------------------------------------------------
    # Metadata Helpers
    # ------------------------------------------------------------------

    def add_tag(
        self,
        tag: str,
    ) -> None:
        """
        Add a tag.
        """

        tag = tag.strip()

        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(
        self,
        tag: str,
    ) -> None:
        """
        Remove a tag.
        """

        if tag in self.tags:
            self.tags.remove(tag)
            self.touch()

    def update_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Update metadata.
        """

        self.metadata[key] = value
        self.touch()

    def remove_metadata(
        self,
        key: str,
    ) -> None:
        """
        Remove metadata entry.
        """

        self.metadata.pop(key, None)
        self.touch()

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def rename(
        self,
        title: str,
    ) -> None:
        """
        Rename research document.
        """

        self.title = title.strip()
        self.touch()

    def clone_metadata(self) -> dict[str, Any]:
        """
        Return a shallow copy of metadata.
        """

        return dict(self.metadata)

    def reset_review(self) -> None:
        """
        Reset review workflow.
        """

        self.status = ResearchStatus.DRAFT
        self.approved = False
        self.verified = False
        self.touch()

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            "Research("
            f"id={self.id}, "
            f"title={self.title!r}, "
            f"sources={self.source_count}, "
            f"findings={self.finding_count}, "
            f"status={self.status.value!r}"
            ")"
        )