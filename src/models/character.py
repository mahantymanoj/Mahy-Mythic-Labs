"""
src/models/character.py

Character entity for Mahy Mythic Labs Studio OS.

A Character is a first-class domain entity representing a recurring
historical, mythological, scientific, fictional, or narrative
character.

The Character entity acts as the single source of truth for:

- Character identity
- Appearance
- Voice
- Personality
- Relationships
- Reference assets
- Continuity requirements

Author
------
Mahy Mythic Labs

Python
------
>=3.11
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from src.models.base import EntityModel
from src.models.components.character_appearance import (
    CharacterAppearance,
)
from src.models.components.continuity import (
    ContinuitySettings,
)
from src.models.components.personality import (
    PersonalityProfile,
)
from src.models.components.reference import (
    ReferenceAsset,
)
from src.models.components.relationship import (
    CharacterRelationship,
)
from src.models.components.voice import (
    VoiceSettings,
)


CharacterType = Literal[
    "historical",
    "mythological",
    "scientific",
    "fictional",
    "narrator",
    "original",
    "other",
]

CanonStatus = Literal[
    "canonical",
    "traditional",
    "interpretation",
    "fictional",
    "unknown",
]

CharacterStatus = Literal[
    "active",
    "inactive",
    "archived",
]


class Character(EntityModel):
    """
    First-class Character entity.

    A Character represents a persistent identity that can appear
    across multiple episodes, scenes and shots.

    Examples
    --------
    - Lord Shiva
    - Lord Krishna
    - Arjuna
    - Ashoka
    - Chanakya
    - Albert Einstein
    - Isaac Newton

    The entity owns identity and lifecycle information while
    reusable characteristics are represented by Value Objects.
    """

    # ==================================================================
    # Identity
    # ==================================================================

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Canonical character name.",
    )

    display_name: str | None = Field(
        default=None,
        max_length=200,
        description="Name displayed in production interfaces.",
    )

    aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names or titles.",
    )

    character_type: CharacterType = Field(
        ...,
        description="Classification of the character.",
    )

    canon_status: CanonStatus = Field(
        default="unknown",
        description="Canonical status of the character.",
    )

    status: CharacterStatus = Field(
        default="active",
        description="Lifecycle status.",
    )

    # ==================================================================
    # Description
    # ==================================================================

    short_description: str | None = Field(
        default=None,
        description="Short character description.",
    )

    biography: str | None = Field(
        default=None,
        description="Detailed character biography.",
    )

    historical_context: str | None = Field(
        default=None,
        description="Historical or mythological context.",
    )

    cultural_context: str | None = Field(
        default=None,
        description="Relevant cultural context.",
    )

    # ==================================================================
    # Core Character Components
    # ==================================================================

    appearance: CharacterAppearance = Field(
        default_factory=CharacterAppearance,
        description="Canonical visual appearance.",
    )

    voice: VoiceSettings = Field(
        default_factory=VoiceSettings,
        description="Canonical voice profile.",
    )

    personality: PersonalityProfile = Field(
        default_factory=PersonalityProfile,
        description="Canonical personality profile.",
    )

    # ==================================================================
    # Relationships
    # ==================================================================

    relationships: list[CharacterRelationship] = Field(
        default_factory=list,
        description="Relationships with other characters.",
    )

    # ==================================================================
    # Reference Assets
    # ==================================================================

    references: list[ReferenceAsset] = Field(
        default_factory=list,
        description="Canonical reference assets.",
    )

    # ==================================================================
    # Continuity
    # ==================================================================

    continuity: ContinuitySettings = Field(
        default_factory=ContinuitySettings,
        description="Character continuity requirements.",
    )

    # ==================================================================
    # Narrative
    # ==================================================================

    motivations: list[str] = Field(
        default_factory=list,
        description="Primary narrative motivations.",
    )

    goals: list[str] = Field(
        default_factory=list,
        description="Character goals.",
    )

    abilities: list[str] = Field(
        default_factory=list,
        description="Known abilities, skills or powers.",
    )

    possessions: list[str] = Field(
        default_factory=list,
        description="Important canonical possessions or props.",
    )

    # ==================================================================
    # Production
    # ==================================================================

    first_episode_id: str | None = Field(
        default=None,
        description="Episode where this character first appears.",
    )

    last_episode_id: str | None = Field(
        default=None,
        description="Most recent episode where this character appears.",
    )

    episode_ids: list[str] = Field(
        default_factory=list,
        description="Episodes in which this character appears.",
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Searchable character tags.",
    )

    notes: str | None = Field(
        default=None,
        description="Internal production notes.",
    )

    # ==================================================================
    # Validation
    # ==================================================================

    @field_validator("name", "display_name")
    @classmethod
    def validate_names(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize character names."""
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "Character name cannot be empty."
            )

        return value

    @field_validator(
        "aliases",
        "episode_ids",
        "tags",
        "motivations",
        "goals",
        "abilities",
        "possessions",
    )
    @classmethod
    def normalize_lists(
        cls,
        values: list[str],
    ) -> list[str]:
        """Remove blank values and normalize whitespace."""
        return [
            value.strip()
            for value in values
            if value.strip()
        ]

    # ==================================================================
    # Identity Helpers
    # ==================================================================

    @property
    def canonical_name(self) -> str:
        """Return the preferred canonical name."""
        return self.display_name or self.name

    @property
    def is_historical(self) -> bool:
        """Return True for historical characters."""
        return self.character_type == "historical"

    @property
    def is_mythological(self) -> bool:
        """Return True for mythological characters."""
        return self.character_type == "mythological"

    @property
    def is_scientific(self) -> bool:
        """Return True for scientific personalities."""
        return self.character_type == "scientific"

    @property
    def is_active(self) -> bool:
        """Return True when the character is active."""
        return self.status == "active"

    # ==================================================================
    # Reference Helpers
    # ==================================================================

    @property
    def canonical_references(self) -> list[ReferenceAsset]:
        """Return canonical reference assets."""
        return [
            reference
            for reference in self.references
            if reference.canonical
        ]

    @property
    def approved_references(self) -> list[ReferenceAsset]:
        """Return approved reference assets."""
        return [
            reference
            for reference in self.references
            if reference.approved
        ]

    def references_for(
        self,
        purpose: str,
    ) -> list[ReferenceAsset]:
        """
        Return references matching a specific purpose.
        """
        return [
            reference
            for reference in self.references
            if reference.purpose == purpose
        ]

    # ==================================================================
    # Relationship Helpers
    # ==================================================================

    def relationships_with(
        self,
        character_id: str,
    ) -> list[CharacterRelationship]:
        """
        Return relationships with a specific character.
        """
        return [
            relationship
            for relationship in self.relationships
            if relationship.target_character_id == character_id
        ]

    def has_relationship_with(
        self,
        character_id: str,
    ) -> bool:
        """Return True when a relationship exists."""
        return bool(
            self.relationships_with(character_id)
        )

    # ==================================================================
    # Episode Helpers
    # ==================================================================

    def appears_in_episode(
        self,
        episode_id: str,
    ) -> bool:
        """Return True when the character appears in an episode."""
        return episode_id in self.episode_ids

    def add_episode(
        self,
        episode_id: str,
    ) -> None:
        """
        Register an episode appearance.

        Duplicate episode IDs are ignored.
        """
        episode_id = episode_id.strip()

        if not episode_id:
            raise ValueError(
                "episode_id cannot be empty."
            )

        if episode_id not in self.episode_ids:
            self.episode_ids.append(episode_id)

        if self.first_episode_id is None:
            self.first_episode_id = episode_id

        self.last_episode_id = episode_id

    # ==================================================================
    # Continuity Helpers
    # ==================================================================

    @property
    def requires_strict_continuity(self) -> bool:
        """Return True when strict continuity is required."""
        return self.continuity.is_strict

    @property
    def canonical_reference_ids(self) -> list[str]:
        """
        Return asset IDs for canonical references.
        """
        return [
            reference.asset_id
            for reference in self.canonical_references
        ]

    # ==================================================================
    # Prompt Generation
    # ==================================================================

    @property
    def appearance_prompt(self) -> str:
        """Return the canonical appearance prompt."""
        return self.appearance.prompt

    @property
    def personality_prompt(self) -> str:
        """Return the canonical personality prompt."""
        return self.personality.prompt

    @property
    def voice_prompt(self) -> str:
        """Return the canonical voice prompt."""
        return self.voice.prompt

    @property
    def continuity_prompt(self) -> str:
        """Return the canonical continuity prompt."""
        return self.continuity.prompt

    def generation_prompt(
        self,
        *,
        include_voice: bool = False,
    ) -> str:
        """
        Build a provider-independent character prompt.

        The provider layer can later transform this into the
        syntax required by Runway, Veo, Kling, Flux, etc.
        """

        parts = [
            self.canonical_name,
            self.appearance_prompt,
            self.personality_prompt,
            self.continuity_prompt,
        ]

        if self.short_description:
            parts.append(self.short_description)

        if self.abilities:
            parts.append(
                "abilities: "
                + ", ".join(self.abilities)
            )

        if self.possessions:
            parts.append(
                "possessions: "
                + ", ".join(self.possessions)
            )

        if include_voice:
            parts.append(self.voice_prompt)

        return ", ".join(
            part
            for part in parts
            if part
        )