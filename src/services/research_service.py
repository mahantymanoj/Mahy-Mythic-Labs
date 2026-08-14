"""
src/services/research_service.py

Research cache service for Mahy Mythic Labs Studio OS.

Persists the reusable content of a Research document (findings,
sources, summary) as a markdown file keyed by topic, so a future
episode covering the same topic can reuse it instead of the
Research Agent re-researching from scratch.

Python
------
>=3.11
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from src.constants import PROJECT_ROOT
from src.models.research import Research, ResearchFinding, ResearchSource
from src.utils.markdown_store import (
    find_markdown_by_slug,
    read_markdown,
    slugify,
    write_markdown,
)

DEFAULT_CACHE_DIRECTORY = PROJECT_ROOT / "knowledge_base" / "research"


# ==============================================================================
# Research Cache Service
# ==============================================================================


class ResearchCacheService:
    """
    Reads and writes topic-keyed research cache files.

    A cache entry stores everything about a Research document that is
    reusable across episodes (findings, sources, summary, notes) but
    deliberately excludes instance-specific fields such as
    project_id/episode_id, which belong to a single production run.
    """

    def __init__(
        self,
        *,
        cache_directory: Path | None = None,
    ) -> None:

        self.cache_directory = (
            cache_directory
            or DEFAULT_CACHE_DIRECTORY
        )

    # ==================================================================
    # Lookup
    # ==================================================================

    def cache_path(
        self,
        topic: str,
    ) -> Path:
        """
        Return the cache file path for a topic (whether or not it exists).
        """

        return self.cache_directory / f"{slugify(topic)}.md"

    def find_cached_path(
        self,
        topic: str,
    ) -> Path | None:
        """
        Return the cache file path for a topic if it already exists.
        """

        return find_markdown_by_slug(
            self.cache_directory,
            slugify(topic),
        )

    def has_cached_research(
        self,
        topic: str,
    ) -> bool:
        """
        Return True when research for this topic has already been cached.
        """

        return self.find_cached_path(topic) is not None

    # ==================================================================
    # Save
    # ==================================================================

    def save(
        self,
        research: Research,
    ) -> Path:
        """
        Persist the reusable content of a Research document to the cache.

        Reused across future calls to save(): reuse_count is preserved
        and incremented so repeated saves for the same topic don't
        reset how often the cache has proven useful.
        """

        path = self.cache_path(research.topic)

        reuse_count = 0

        if path.is_file():
            existing_metadata, _ = read_markdown(path)
            reuse_count = int(
                existing_metadata.get("reuse_count", 0)
            )

        metadata: dict[str, Any] = {
            "topic": research.topic,
            "title": research.title,
            "status": research.status,
            "confidence_score": research.confidence_score,
            "completeness_score": research.completeness_score,
            "tags": list(research.tags),
            "keywords": list(research.keywords),
            "assumptions": list(research.assumptions),
            "findings": [
                finding.model_dump(mode="json")
                for finding in research.findings
            ],
            "sources": [
                source.model_dump(mode="json")
                for source in research.sources
            ],
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "reuse_count": reuse_count,
        }

        body_parts = [f"# {research.title}", ""]

        if research.summary:
            body_parts += ["## Summary", "", research.summary, ""]

        if research.objective:
            body_parts += ["## Objective", "", research.objective, ""]

        if research.notes:
            body_parts += ["## Notes", "", research.notes, ""]

        body = "\n".join(body_parts).strip() + "\n"

        return write_markdown(
            path,
            metadata=metadata,
            body=body,
        )

    # ==================================================================
    # Load
    # ==================================================================

    def load_cache_data(
        self,
        topic: str,
    ) -> dict[str, Any] | None:
        """
        Return the raw cached metadata for a topic, or None if not cached.
        """

        path = self.find_cached_path(topic)

        if path is None:
            return None

        metadata, body = read_markdown(path)

        metadata["body"] = body

        return metadata

    def load_as_research(
        self,
        topic: str,
        *,
        project_id: UUID,
        episode_id: UUID,
        title: str | None = None,
    ) -> Research | None:
        """
        Build a new Research entity for a new episode, pre-filled from
        the cache for this topic.

        Returns None when nothing is cached for this topic (the caller
        should fall back to running the Research Agent).
        """

        data = self.load_cache_data(topic)

        if data is None:
            return None

        path = self.find_cached_path(topic)

        findings = [
            ResearchFinding.model_validate(item)
            for item in data.get("findings", [])
        ]

        sources = [
            ResearchSource.model_validate(item)
            for item in data.get("sources", [])
        ]

        summary, objective, notes = self._parse_body_sections(
            data.get("body", "")
        )

        research = Research(
            project_id=project_id,
            episode_id=episode_id,
            title=title or data.get("title", topic),
            topic=data.get("topic", topic),
            summary=summary,
            objective=objective,
            notes=notes,
            findings=findings,
            sources=sources,
            assumptions=list(data.get("assumptions", [])),
            keywords=list(data.get("keywords", [])),
            tags=list(data.get("tags", [])),
            confidence_score=data.get("confidence_score", 5.0),
            completeness_score=data.get("completeness_score", 0.0),
        )

        research.update_metadata("reused_from_cache", True)
        research.update_metadata("cache_source", str(path))

        self._bump_reuse_count(path)

        return research

    # ==================================================================
    # Internal Helpers
    # ==================================================================

    @staticmethod
    def _parse_body_sections(
        body: str,
    ) -> tuple[str | None, str | None, str | None]:
        """
        Extract Summary / Objective / Notes sections from the markdown body.
        """

        sections: dict[str, list[str]] = {}
        current: str | None = None

        for line in body.splitlines():

            stripped = line.strip()

            if stripped.startswith("## "):
                current = stripped[3:].strip().lower()
                sections[current] = []
                continue

            if stripped.startswith("# "):
                current = None
                continue

            if current is not None:
                sections[current].append(line)

        def joined(key: str) -> str | None:
            lines = sections.get(key)

            if not lines:
                return None

            text = "\n".join(lines).strip()

            return text or None

        return (
            joined("summary"),
            joined("objective"),
            joined("notes"),
        )

    def _bump_reuse_count(
        self,
        path: Path,
    ) -> None:
        """
        Increment the reuse_count of a cache file after it is loaded.
        """

        metadata, body = read_markdown(path)

        metadata["reuse_count"] = int(
            metadata.get("reuse_count", 0)
        ) + 1

        metadata["last_reused_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        write_markdown(
            path,
            metadata=metadata,
            body=body,
        )
