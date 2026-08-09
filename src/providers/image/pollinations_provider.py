"""Free Pollinations.ai image provider for Mahy Mythic Labs."""

from __future__ import annotations

import urllib.parse
from pathlib import Path
from typing import Optional

import requests

from src.enums import ProviderBackend, ProviderType


class PollinationsImageProvider:
    """Free Image Generation Provider via Pollinations.ai (No API key needed)."""

    BASE_URL = "https://image.pollinations.ai/prompt"

    def __init__(self, default_model: str = "flux") -> None:
        self.default_model = default_model
        self.backend = ProviderBackend.FREE_POLLINATIONS
        self.provider_type = ProviderType.IMAGE

    def generate(
        self,
        prompt: str,
        output_path: str | Path,
        *,
        width: int = 1080,
        height: int = 1920,
        seed: Optional[int] = 42,
    ) -> Path:
        """Generate image and save directly to file."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        encoded_prompt = urllib.parse.quote(prompt)
        url = f"{self.BASE_URL}/{encoded_prompt}?width={width}&height={height}&model={self.default_model}&seed={seed}&nologo=true"

        response = requests.get(url, timeout=90)
        response.raise_for_status()

        output.write_bytes(response.content)
        return output


if __name__ == "__main__":
    provider = PollinationsImageProvider()
    out = provider.generate(
        "Cinematic bronze Antikythera mechanism on museum table, dark dramatic lighting",
        "assets/images/test_pollinations.png",
        width=1080,
        height=1920,
    )
    print(f"Pollinations Image Saved: {out}")
