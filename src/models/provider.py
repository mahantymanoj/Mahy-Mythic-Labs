"""
src/models/provider.py

Domain models representing AI providers and their capabilities.

These models are configuration and metadata only.  They do NOT contain
provider-specific API logic.  The implementation of providers belongs in
src/providers/.

Compatible with:
    - Pydantic v2
    - Python 3.11+
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field, field_validator

from .base import EntityModel, ValueModel


# ==============================================================================
# Enums
# ==============================================================================


class ProviderType(str, Enum):
    """Supported provider categories."""

    LLM = "llm"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    EMBEDDING = "embedding"
    MODERATION = "moderation"
    OCR = "ocr"


class ProviderStatus(str, Enum):
    """Provider availability."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class Capability(str, Enum):
    """Provider capabilities."""

    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    IMAGE_EDITING = "image_editing"
    VIDEO_EDITING = "video_editing"
    UPSCALING = "upscaling"
    INPAINTING = "inpainting"


# ==============================================================================
# Supporting Value Objects (immutable, compared by value, no touch())
# ==============================================================================


class RateLimit(ValueModel):
    """Provider rate limits — immutable value object."""

    requests_per_minute: Optional[int] = Field(default=None, ge=1)
    requests_per_hour: Optional[int] = Field(default=None, ge=1)
    requests_per_day: Optional[int] = Field(default=None, ge=1)


class Pricing(ValueModel):
    """
    Pricing information — immutable value object.
    Currency is informational only.
    """

    currency: str = "USD"
    input_cost: float = Field(default=0.0, ge=0.0)
    output_cost: float = Field(default=0.0, ge=0.0)
    image_cost: float = Field(default=0.0, ge=0.0)
    video_cost: float = Field(default=0.0, ge=0.0)
    audio_cost: float = Field(default=0.0, ge=0.0)

    @property
    def total_per_call(self) -> float:
        return round(self.input_cost + self.output_cost, 6)


class ModelInfo(ValueModel):
    """
    Information about one model offered by a provider.
    Immutable value object — compared by value.
    """

    name: str
    display_name: Optional[str] = None
    version: Optional[str] = None
    context_window: Optional[int] = Field(default=None, ge=1)
    max_output_tokens: Optional[int] = Field(default=None, ge=1)
    supports_streaming: bool = False
    supports_json: bool = False
    supports_tools: bool = False
    supports_vision: bool = False


# ==============================================================================
# Provider Entity (has identity, lifecycle, touch())
# ==============================================================================


class Provider(EntityModel):
    """
    Metadata describing an AI provider.

    Uses EntityModel because Provider records have persistent identity
    and are tracked across the system lifecycle.

    Examples
    --------
    - OpenAI
    - Anthropic
    - Google
    - xAI
    - Runway
    - Kling
    - Veo
    """

    name: str = Field(..., min_length=2)

    display_name: Optional[str] = None

    provider_type: ProviderType = Field(...)

    status: ProviderStatus = ProviderStatus.ENABLED

    priority: int = Field(default=100, ge=1)

    enabled: bool = True

    endpoint: Optional[str] = None

    api_version: Optional[str] = None

    supported_models: List[ModelInfo] = Field(default_factory=list)

    capabilities: List[Capability] = Field(default_factory=list)

    rate_limit: Optional[RateLimit] = None

    pricing: Optional[Pricing] = None

    metadata: Dict[str, str] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_available(self) -> bool:
        """True if the provider can currently be used."""
        return (
            self.enabled
            and self.status == ProviderStatus.ENABLED
        )

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def supports(self, capability: Capability) -> bool:
        """Check whether the provider supports a capability."""
        return capability in self.capabilities

    def add_model(self, model: ModelInfo) -> None:
        """Register a supported model."""
        self.supported_models.append(model)
        self.touch()

    def add_capability(self, capability: Capability) -> None:
        """Register a new capability."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.touch()

    def disable(self) -> None:
        """Disable the provider."""
        self.enabled = False
        self.status = ProviderStatus.DISABLED
        self.touch()

    def enable(self) -> None:
        """Enable the provider."""
        self.enabled = True
        self.status = ProviderStatus.ENABLED
        self.touch()
