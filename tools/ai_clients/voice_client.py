"""Client for generating narration audio files."""

from __future__ import annotations

import os
from pathlib import Path

from openai import OpenAI


class VoiceClient:
    """Generate a narration file from approved script text."""

    def __init__(
        self,
        model: str | None = None,
        voice: str | None = None,
    ) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set.")

        self.client = OpenAI()
        self.model = model or os.getenv("MAHY_VOICE_MODEL", "gpt-4o-mini-tts")
        self.voice = voice or os.getenv("MAHY_VOICE", "marin")

    def generate(
        self,
        text: str,
        output_path: str | Path,
        *,
        instructions: str = (
            "Speak with calm cinematic documentary pacing. "
            "Use clear pronunciation, restrained emotion, and natural pauses."
        ),
    ) -> Path:
        """Generate narration and stream it directly to an audio file."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=self.voice,
            input=text,
            instructions=instructions,
            response_format="wav",
        ) as response:
            response.stream_to_file(output)

        return output


if __name__ == "__main__":
    client = VoiceClient()

    path = client.generate(
        text=(
            "From a shipwreck came a bronze mechanism built "
            "to model the rhythms of the sky."
        ),
        output_path="assets/audio/narration/ep001-narration-v01.wav",
    )

    print(f"Saved narration: {path}")