"""Google Gemini LLM provider for Mahy Mythic Labs."""

from __future__ import annotations

import os
from typing import Optional

import requests

from src.enums import ProviderBackend, ProviderType


class GoogleGeminiProvider:
    """Free Tier LLM provider powered by Google Gemini API."""

    def __init__(self, model: str = "gemini-1.5-flash") -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model = os.getenv("MAHY_GEMINI_MODEL", model)
        self.backend = ProviderBackend.FREE_GEMINI
        self.provider_type = ProviderType.LLM

    def generate(
        self,
        prompt: str,
        *,
        instructions: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate structured text using Google Gemini API."""
        if not self.api_key:
            # Fallback mock mode if no API key is exported yet
            return f"[Gemini Mock Response for: {prompt[:60]}...]"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        system_instruction = instructions or "You are the Mahy Mythic Labs documentary writing assistant."
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"System Instructions: {system_instruction}\n\nUser Request: {prompt}"}],
                }
            ],
            "generationConfig": {"temperature": temperature},
        }

        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as err:
            raise RuntimeError(f"Unexpected response structure from Gemini API: {data}") from err


if __name__ == "__main__":
    provider = GoogleGeminiProvider()
    res = provider.generate("Give me 3 short video hooks about ancient Greek astronomy.")
    print(res)
