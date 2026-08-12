"""Free Edge-TTS audio provider for Mahy Mythic Labs."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import edge_tts

from src.enums import ProviderBackend, ProviderType


class EdgeTTSProvider:
    """Free TTS provider powered by Microsoft Edge TTS (no API key required)."""

    def __init__(self, default_voice: str = "en-US-ChristopherNeural") -> None:
        self.default_voice = default_voice
        self.backend = ProviderBackend.FREE_EDGE_TTS
        self.provider_type = ProviderType.AUDIO

    async def generate_audio_async(
        self,
        text: str,
        output_path: str | Path,
        voice: Optional[str] = None,
    ) -> Path:
        """Asynchronously generate an audio file using Edge TTS."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        selected_voice = voice or self.default_voice

        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(str(output))
        return output

    def generate(
        self,
        text: str,
        output_path: str | Path,
        voice: Optional[str] = None,
    ) -> Path:
        """Synchronous wrapper around Edge TTS generation."""
        return asyncio.run(self.generate_audio_async(text, output_path, voice))


if __name__ == "__main__":
    provider = EdgeTTSProvider()
    out = provider.generate(
        "Welcome to Mahy Mythic Labs. Exploring the mysteries of the universe.",
        "assets/audio/test_edge_tts.mp3",
    )
    print(f"Edge TTS Generated: {out}")
