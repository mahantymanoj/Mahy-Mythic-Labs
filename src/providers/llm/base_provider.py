"""
src/providers/base_provider.py

Abstract base class for all AI providers.

Every provider implementation (OpenAI, Anthropic, Google,
xAI, Runway, ElevenLabs, etc.) must inherit from BaseProvider.

Responsibilities
----------------
• Authentication
• Health checks
• Model discovery
• Capability reporting
• Text generation
• Image generation
• Video generation
• Audio generation
• Embeddings
• Cost estimation

This module defines only the provider contract.
No provider-specific implementation belongs here.

Python
------
>=3.11
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ==============================================================================
# Enums
# ==============================================================================


class ProviderType(str, Enum):
    """
    Supported AI providers.
    """

    OPENAI = "openai"

    ANTHROPIC = "anthropic"

    GOOGLE = "google"

    XAI = "xai"

    STABILITY = "stability"

    RUNWAY = "runway"

    ELEVENLABS = "elevenlabs"

    KLING = "kling"

    CUSTOM = "custom"


class ProviderCapability(str, Enum):
    """
    Provider capabilities.
    """

    TEXT = "text"

    IMAGE = "image"

    VIDEO = "video"

    AUDIO = "audio"

    EMBEDDING = "embedding"

    MODERATION = "moderation"

# ==============================================================================
# Provider Configuration
# ==============================================================================


class ProviderConfig(BaseModel):
    """
    Configuration shared by every provider.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    provider: ProviderType

    api_key: str

    organization: str | None = None

    base_url: str | None = None

    timeout: float = Field(
        default=300.0,
        gt=0,
    )

    max_retries: int = Field(
        default=3,
        ge=0,
    )

    enabled: bool = True

    default_model: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    # ==============================================================================
# Provider Response Models
# ==============================================================================


class ProviderUsage(BaseModel):
    """
    Token/resource usage returned by a provider.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    prompt_tokens: int = Field(
        default=0,
        ge=0,
    )

    completion_tokens: int = Field(
        default=0,
        ge=0,
    )

    total_tokens: int = Field(
        default=0,
        ge=0,
    )

    estimated_cost: float = Field(
        default=0.0,
        ge=0,
    )


class ProviderError(BaseModel):
    """
    Standardized provider error.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    code: str

    message: str

    provider: ProviderType

    retryable: bool = False

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ProviderResponse(BaseModel):
    """
    Standard response returned by every provider.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    success: bool = True

    provider: ProviderType

    model: str

    output: Any | None = None

    finish_reason: str | None = None

    usage: ProviderUsage | None = None

    error: ProviderError | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @property
    def failed(self) -> bool:
        """
        Whether the request failed.
        """
        return not self.success

    @property
    def has_usage(self) -> bool:
        """
        Whether usage information is available.
        """
        return self.usage is not None

    @property
    def has_error(self) -> bool:
        """
        Whether an error is available.
        """
        return self.error is not None
    # ==============================================================================
# Base Provider
# ==============================================================================


class BaseProvider(ABC):
    """
    Abstract base class for every AI provider.

    Every provider implementation must inherit from this class.
    """

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(self) -> ProviderType:
        """
        Provider type.
        """
        return self.config.provider

    @property
    def default_model(self) -> str | None:
        """
        Default model configured for this provider.
        """
        return self.config.default_model

    @property
    def enabled(self) -> bool:
        """
        Whether the provider is enabled.
        """
        return self.config.enabled

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Validate provider credentials.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify provider availability.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------

    @abstractmethod
    async def list_models(
        self,
    ) -> list[str]:
        """
        Return available models.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    @abstractmethod
    def capabilities(
        self,
    ) -> set[ProviderCapability]:
        """
        Return supported capabilities.
        """
        raise NotImplementedError

    def supports(
        self,
        capability: ProviderCapability,
    ) -> bool:
        """
        Check capability support.
        """

        return capability in self.capabilities()

        # ------------------------------------------------------------------
    # Text Generation
    # ------------------------------------------------------------------

    @abstractmethod
    async def close(self) -> None:
        """
        Release provider resources.

        Examples
        --------
        - Close HTTP clients
        - Close WebSocket connections
        - Flush pending requests
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate text.
        """
        raise NotImplementedError

    @abstractmethod
    async def stream_text(
        self,
        prompt: str,
        **kwargs: Any,
    ):
        """
        Stream generated text.

        Returns
        -------
        AsyncIterator[str]
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Image Generation
    # ------------------------------------------------------------------

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate an image.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Video Generation
    # ------------------------------------------------------------------

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate a video.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Audio Generation
    # ------------------------------------------------------------------

    @abstractmethod
    async def generate_audio(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate audio.
        """
        raise NotImplementedError

    @abstractmethod
    async def text_to_speech(
        self,
        text: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Convert text to speech.
        """
        raise NotImplementedError

    @abstractmethod
    async def speech_to_text(
        self,
        audio: bytes | str,
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Convert speech to text.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    @abstractmethod
    async def generate_embeddings(
        self,
        text: str | list[str],
        **kwargs: Any,
    ) -> ProviderResponse:
        """
        Generate embeddings.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def validate_prompt(
        self,
        prompt: str,
    ) -> str:
        """
        Validate a prompt before sending it to a provider.
        """

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Prompt cannot be empty."
            )

        return prompt

    def validate_model(
        self,
        model: str | None,
    ) -> str:
        """
        Resolve the model to use.
        """

        resolved = model or self.default_model

        if not resolved:
            raise ValueError(
                "No model specified."
            )

        return resolved

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"provider={self.provider.value!r}, "
            f"default_model={self.default_model!r})"
        )