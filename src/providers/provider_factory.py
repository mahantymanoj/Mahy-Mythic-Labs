"""Provider Factory for Mahy Mythic Labs."""

from __future__ import annotations

from typing import Any

from src.enums import ProviderType
from src.providers.audio.edge_tts_provider import EdgeTTSProvider
from src.providers.image.pollinations_provider import PollinationsImageProvider
from src.providers.llm.google_provider import GoogleGeminiProvider


class ProviderFactory:
    """Factory creating default free providers with fallback capabilities."""

    @staticmethod
    def get_audio_provider() -> EdgeTTSProvider:
        """Return free Edge-TTS audio provider."""
        return EdgeTTSProvider()

    @staticmethod
    def get_llm_provider() -> GoogleGeminiProvider:
        """Return free Google Gemini / local LLM provider."""
        return GoogleGeminiProvider()

    @staticmethod
    def get_image_provider() -> PollinationsImageProvider:
        """Return free Pollinations image provider."""
        return PollinationsImageProvider()
