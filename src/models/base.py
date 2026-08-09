"""
src/models/base.py

Base domain models for Mahy Mythic Labs Studio OS.

This module provides the foundational classes for all domain models
following Domain-Driven Design (DDD) principles.

Hierarchy
---------
BaseDomainModel
├── ValueModel
└── EntityModel

EntityModel
-----------
Represents objects with identity.

Examples
--------
- Project
- Episode
- Research
- Script
- Storyboard
- Scene
- Shot
- Asset
- Workflow
- Character

ValueModel
----------
Represents immutable value objects.

Examples
--------
- CameraSettings
- LightingSettings
- PromptSet
- Timing
- RateLimit
- Pricing
- TokenUsage
- GenerationParameters
- Metadata
- VoiceSettings
- PersonalityProfile
- ContinuitySettings

Author
------
Mahy Mythic Labs

Python
------
>=3.11

Pydantic
--------
>=2.x
"""

from __future__ import annotations

from abc import ABC
from datetime import UTC, datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# Shared Configuration
# ==============================================================================

DEFAULT_MODEL_CONFIG: ConfigDict = ConfigDict(
    extra="forbid",
    validate_assignment=True,
    validate_default=True,
    populate_by_name=True,
    use_enum_values=True,
    arbitrary_types_allowed=False,
    frozen=False,
    str_strip_whitespace=True,
)


# ==============================================================================
# Utility Functions
# ==============================================================================


def utc_now() -> datetime:
    """
    Return the current timezone-aware UTC datetime.

    Returns
    -------
    datetime
        Current UTC timestamp.
    """
    return datetime.now(UTC)


def _make_hashable(value: Any) -> Any:
    """
    Convert nested Python values into hashable representations.

    This is used by ValueModel.__hash__().

    Supports
    --------
    - None
    - bool
    - int
    - float
    - str
    - bytes
    - UUID
    - datetime
    - list
    - tuple
    - set
    - dict
    - Pydantic models

    Parameters
    ----------
    value:
        Value to convert.

    Returns
    -------
    Any
        Hashable representation.
    """

    if isinstance(value, dict):
        return tuple(
            sorted(
                (
                    str(key),
                    _make_hashable(item),
                )
                for key, item in value.items()
            )
        )

    if isinstance(value, (list, tuple)):
        return tuple(
            _make_hashable(item)
            for item in value
        )

    if isinstance(value, set):
        return frozenset(
            _make_hashable(item)
            for item in value
        )

    if isinstance(value, BaseModel):
        return _make_hashable(
            value.model_dump(
                mode="python",
                exclude_none=False,
            )
        )

    if isinstance(value, (datetime, UUID)):
        return str(value)

    try:
        hash(value)
        return value
    except TypeError:
        return repr(value)


# ==============================================================================
# Base Domain Model
# ==============================================================================


class BaseDomainModel(BaseModel, ABC):
    """
    Root class for every Studio OS domain model.

    Responsibilities
    ----------------
    - Common Pydantic configuration
    - Serialization helpers
    - Deserialization helpers
    - Copy helpers
    - Update helpers
    - Consistent representation

    Notes
    -----
    This class intentionally does NOT define:

    - id
    - created_at
    - updated_at
    - version

    Those belong only to EntityModel.
    """

    model_config: ClassVar[ConfigDict] = DEFAULT_MODEL_CONFIG

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def model_name(self) -> str:
        """
        Return the model class name.

        Examples
        --------
        Episode
        Research
        CameraSettings
        """
        return self.__class__.__name__

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(
        self,
        *,
        exclude_none: bool = True,
        exclude_defaults: bool = False,
        exclude_unset: bool = False,
        by_alias: bool = True,
    ) -> dict[str, Any]:
        """
        Convert the model into a Python dictionary.

        Parameters
        ----------
        exclude_none:
            Exclude fields whose value is None.

        exclude_defaults:
            Exclude fields whose value equals the default.

        exclude_unset:
            Exclude fields that were not explicitly provided.

        by_alias:
            Use Pydantic field aliases where available.

        Returns
        -------
        dict[str, Any]
            Serialized model.
        """

        return self.model_dump(
            mode="python",
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            exclude_unset=exclude_unset,
            by_alias=by_alias,
        )

    def to_json(
        self,
        *,
        indent: int | None = 2,
        exclude_none: bool = True,
        exclude_defaults: bool = False,
        exclude_unset: bool = False,
        by_alias: bool = True,
    ) -> str:
        """
        Serialize the model into JSON.

        Parameters
        ----------
        indent:
            JSON indentation level.

        exclude_none:
            Exclude None values.

        exclude_defaults:
            Exclude values equal to defaults.

        exclude_unset:
            Exclude fields not explicitly provided.

        by_alias:
            Use field aliases.

        Returns
        -------
        str
            JSON representation.
        """

        return self.model_dump_json(
            indent=indent,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            exclude_unset=exclude_unset,
            by_alias=by_alias,
        )

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> BaseDomainModel:
        """
        Create a model from a dictionary.

        Parameters
        ----------
        data:
            Source dictionary.

        Returns
        -------
        BaseDomainModel
            Validated model instance.
        """

        return cls.model_validate(data)

    @classmethod
    def from_json(
        cls,
        json_data: str,
    ) -> BaseDomainModel:
        """
        Create a model from JSON.

        Parameters
        ----------
        json_data:
            JSON string.

        Returns
        -------
        BaseDomainModel
            Validated model instance.
        """

        return cls.model_validate_json(json_data)

    # ------------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------------

    def clone(
        self,
        **updates: Any,
    ) -> BaseDomainModel:
        """
        Create a deep copy of the model.

        Optional updates can be applied to the copied model.

        Example
        -------
        new_scene = scene.clone(
            title="New Scene"
        )
        """

        return self.model_copy(
            deep=True,
            update=updates,
        )

    def copy_with(
        self,
        **changes: Any,
    ) -> BaseDomainModel:
        """
        Create a deep copy with updated values.

        Example
        -------
        new_scene = scene.copy_with(
            title="Opening Scene"
        )
        """

        return self.model_copy(
            update=changes,
            deep=True,
        )

    # ------------------------------------------------------------------
    # Update Helpers
    # ------------------------------------------------------------------

    def update(
        self,
        **changes: Any,
    ) -> None:
        """
        Update fields in-place.

        Pydantic's validate_assignment configuration ensures
        assignments are validated.

        Raises
        ------
        AttributeError
            If a field does not exist.
        """

        model_fields = type(self).model_fields

        for field_name, value in changes.items():

            if field_name not in model_fields:
                raise AttributeError(
                    f"{self.model_name} has no field "
                    f"'{field_name}'."
                )

            setattr(
                self,
                field_name,
                value,
            )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Return the model name."""
        return self.model_name

    def __repr__(self) -> str:
        """Return a useful developer representation."""
        return (
            f"{self.model_name}("
            f"{self.to_dict()}"
            f")"
        )


# ==============================================================================
# Value Model
# ==============================================================================


class ValueModel(BaseDomainModel):
    """
    Base class for Domain-Driven Design Value Objects.

    Characteristics
    --------------
    - No identity
    - No UUID
    - No timestamps
    - Compared by value
    - Immutable

    Examples
    --------
    - CameraSettings
    - LightingSettings
    - PromptSet
    - Timing
    - Pricing
    - RateLimit
    - TokenUsage
    - VoiceSettings
    - PersonalityProfile
    - ContinuitySettings
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=False,
        frozen=True,
        str_strip_whitespace=True,
    )

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """
        Compare value objects by their complete value.

        Two value objects are equal when they are the same class
        and contain the same field values.
        """

        if not isinstance(other, self.__class__):
            return False

        return (
            self.model_dump(
                mode="python",
                exclude_none=False,
            )
            == other.model_dump(
                mode="python",
                exclude_none=False,
            )
        )

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def __hash__(self) -> int:
        """
        Generate a stable hash from the complete value.

        Nested lists and dictionaries are converted into immutable
        representations so ValueModels containing collection fields
        can still be used safely in sets and as dictionary keys.
        """

        values = _make_hashable(
            self.model_dump(
                mode="python",
                exclude_none=False,
            )
        )

        return hash(
            (
                self.__class__,
                values,
            )
        )

    # ------------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------------

    def replace(
        self,
        **changes: Any,
    ) -> ValueModel:
        """
        Return a modified copy.

        The original object remains unchanged.

        Example
        -------
        camera2 = camera.replace(
            lens="50mm"
        )
        """

        return self.model_copy(
            update=changes,
            deep=True,
        )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a useful developer representation."""
        return (
            f"{self.model_name}("
            f"{self.to_dict()}"
            f")"
        )


# ==============================================================================
# Entity Model
# ==============================================================================


class EntityModel(BaseDomainModel):
    """
    Base class for all Studio OS domain entities.

    Unlike ValueModel, EntityModel has persistent identity.

    Entity identity is represented by UUID.

    Examples
    --------
    - Project
    - Episode
    - Research
    - Script
    - Storyboard
    - Scene
    - Shot
    - Asset
    - Character
    - Workflow
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    id: UUID = Field(
        default_factory=uuid4,
        description="Globally unique entity identifier.",
    )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    created_at: datetime = Field(
        default_factory=utc_now,
        description="Entity creation timestamp in UTC.",
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        description="Last modification timestamp in UTC.",
    )

    version: int = Field(
        default=1,
        ge=1,
        description="Entity version number.",
    )

    # ------------------------------------------------------------------
    # Lifecycle Helpers
    # ------------------------------------------------------------------

    def touch(self) -> None:
        """
        Update the entity's modification timestamp.

        This does not change the entity version.
        """

        self.updated_at = utc_now()

    def bump_version(self) -> None:
        """
        Increment the entity version and update its timestamp.
        """

        self.version += 1
        self.touch()

    # ------------------------------------------------------------------
    # Update Helpers
    # ------------------------------------------------------------------

    def update(
        self,
        **changes: Any,
    ) -> None:
        """
        Update entity fields and refresh updated_at.

        The entity version is intentionally NOT incremented here.

        Version management remains explicit through bump_version().
        """

        super().update(**changes)
        self.touch()

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """
        Compare entities by identity.

        Two different entities with identical field values are
        still considered different if their IDs differ.
        """

        if not isinstance(other, EntityModel):
            return NotImplemented

        return self.id == other.id

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def __hash__(self) -> int:
        """
        Hash the entity using its UUID identity.
        """

        return hash(
            (
                self.__class__,
                self.id,
            )
        )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a concise entity representation."""
        return (
            f"{self.model_name}("
            f"id={self.id}, "
            f"version={self.version}"
            f")"
        )