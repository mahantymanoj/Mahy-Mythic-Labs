"""
src/providers/base_provider.py

Universal provider contract for Studio OS.

All concrete providers (OpenAI, Anthropic, Google, xAI, Flux, Veo, etc.)
implement this interface.

Python
------
>=3.11
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class ProviderType(str, Enum):
    """Supported provider types."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"
    FLUX = "flux"
    IDEOGRAM = "ideogram"
    RECRAFT = "recraft"
    GEMINI_IMAGE = "gemini_image"
    POLLINATIONS = "pollinations"
    VEO = "veo"
    RUNWAY = "runway"
    KLING = "kling"
    HAILUO = "hailuo"
    ELEVENLABS = "elevenlabs"
    AZURE_TTS = "azure_tts"
    OPENAI_TTS = "openai_tts"
    EDGE_TTS = "edge_tts"
    MUSIC = "music"


class ProviderCapability(str, Enum):
    """Provider capabilities."""

    TEXT = "text"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_EDITING = "image_editing"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    TEXT_TO_SPEECH = "text_to_speech"
    SPEECH_TO_TEXT = "speech_to_text"
    MUSIC_GENERATION = "music_generation"


@dataclass
class ProviderConfig:
    """Provider configuration."""

    provider: ProviderType
    api_key: str = ""
    base_url: str | None = None
    organization: str | None = None
    project: str | None = None
    timeout: int = 120
    max_retries: int = 3
    default_model: str | None = None

    # Extra provider-specific config
    extra: dict[str, Any] = None

    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


@dataclass
class ProviderUsage:
    """Token usage information."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Cost estimation (USD)
    estimated_cost_usd: float = 0.0


@dataclass
class ProviderError:
    """Provider error information."""

    code: str
    message: str
    provider: ProviderType
    retryable: bool = False
    details: dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class ProviderResponse:
    """Standardized provider response."""

    success: bool
    provider: ProviderType
    model: str
    output: Any = None
    finish_reason: str | None = None
    usage: ProviderUsage | None = None
    error: ProviderError | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseProvider:
    """
    Abstract base class for all AI providers.

    Providers handle:
    - Authentication and configuration
    - Health checks
    - Capability reporting
    - Model listing
    - Text/image/video/audio generation
    - Streaming
    - Token counting
    - Resource cleanup
    """

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self._initialized = False

    @property
    def provider_type(self) -> ProviderType:
        return self.config.provider

    @property
    def default_model(self) -> str:
        return self.config.default_model or ""

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def initialize(self) -> bool:
        """Initialize the provider. Returns True on success."""
        self._initialized = True
        return await self.authenticate()

    async def authenticate(self) -> bool:
        """Validate credentials. Override in subclass."""
        return True

    async def health_check(self) -> bool:
        """Verify provider is reachable. Override in subclass."""
        return await self.authenticate()

    async def close(self) -> None:
        """Release resources. Override in subclass."""
        pass

    # =========================================================================
    # Capabilities
    # =========================================================================

    def capabilities(self) -> set[ProviderCapability]:
        """Return supported capabilities. Override in subclass."""
        return set()

    async def list_models(self) -> list[str]:
        """List available models. Override in subclass."""
        return []

    # =========================================================================
    # Validation Helpers
    # =========================================================================

    def validate_prompt(self, prompt: str) -> str:
        """Validate and normalize prompt."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        return prompt.strip()

    def validate_model(self, model: str | None) -> str:
        """Validate and resolve model name."""
        if model:
            return model
        if self.default_model:
            return self.default_model
        raise ValueError("No model specified and no default model configured")

    # =========================================================================
    # Error Response Helper
    # =========================================================================

    def _error_response(
        self,
        model: str,
        code: str,
        message: str,
        retryable: bool,
    ) -> ProviderResponse:
        return ProviderResponse(
            success=False,
            provider=self.provider_type,
            model=model,
            error=ProviderError(
                code=code,
                message=message,
                provider=self.provider_type,
                retryable=retryable,
            ),
        )

    # =========================================================================
    # Abstract Methods (to be implemented by subclasses)
    # =========================================================================

    async def generate_text(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        raise NotImplementedError

    async def stream_text(
        self,
        prompt: str,
        **kwargs: Any,
    ):
        raise NotImplementedError

    async def generate_embeddings(
        self,
        text: str | list[str],
        **kwargs: Any,
    ) -> ProviderResponse:
        raise NotImplementedError

    async def count_tokens(
        self,
        text: str,
        model: str | None = None,
    ) -> int:
        raise NotImplementedError

    async def generate_image(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        raise NotImplementedError

    async def generate_video(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        raise NotImplementedError

    async def generate_audio(
        self,
        text: str,
        **kwargs: Any,
    ) -> ProviderResponse:
        raise NotImplementedError