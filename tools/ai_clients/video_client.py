"""Client for creating, checking, and downloading video-generation jobs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


class VideoClient:
    """Minimal REST client for asynchronous video-generation jobs."""

    API_BASE_URL = "https://api.openai.com/v1"
   
    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        self.model = model or os.getenv("MAHY_VIDEO_MODEL", "sora-2")
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def create_job(
        self,
        prompt: str,
        *,
        seconds: int = 8,
        size: str = "1280x720",
        reference_image: str | Path | None = None,
    ) -> dict[str, Any]:
        """Create a video job and return its API response."""
        data = {
            "model": self.model,
            "prompt": prompt,
            "seconds": str(seconds),
            "size": size,
        }

        files = None
        if reference_image:
            image_path = Path(reference_image)
            files = {
                "input_reference": (
                    image_path.name,
                    image_path.read_bytes(),
                    "image/png",
                )
            }

        response = requests.post(
            f"{self.API_BASE_URL}/videos",
            headers=self.headers,
            data=data,
            files=files,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def get_job(self, video_id: str) -> dict[str, Any]:
        """Return the latest job status and metadata."""
        response = requests.get(
            f"{self.API_BASE_URL}/videos/{video_id}",
            headers=self.headers,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def download(self, video_id: str, output_path: str | Path) -> Path:
        """Download a completed video to the requested local path."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(
            f"{self.API_BASE_URL}/videos/{video_id}/content",
            headers=self.headers,
            timeout=300,
        )
        response.raise_for_status()
        output.write_bytes(response.content)
        return output


if __name__ == "__main__":
    client = VideoClient()

    job = client.create_job(
        prompt=(
            "Slow cinematic macro orbit around an ancient Greek bronze "
            "astronomical mechanism. Realistic corroded metal, warm museum "
            "lighting, dark background, physically plausible turning gears, "
            "no text, no logo, no fantasy elements."
        ),
        seconds=8,
        size="1280x720",
    )

    print(job)