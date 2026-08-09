"""Client for generating and saving Mahy Mythic Labs image assets."""

from __future__ import annotations

import base64
import os
from pathlib import Path

from openai import OpenAI


class ImageClient:
    """Generate a still image and save it to a local PNG file."""

    def __init__(self, model: str | None = None) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set.")

        self.client = OpenAI()
        self.model = model or os.getenv("MAHY_IMAGE_MODEL", "gpt-image-2")

    def generate(
        self,
        prompt: str,
        output_path: str | Path,
        *,
        size: str = "1536x1024",
    ) -> Path:
        """Generate one image and return the saved file path."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            response_format="b64_json",
        )
        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise RuntimeError("Image generation returned no image data.")

        output.write_bytes(base64.b64decode(image_base64))
        return output


if __name__ == "__main__":
    client = ImageClient()

    path = client.generate(
        prompt=(
            "Cinematic documentary still of an ancient bronze astronomical "
            "mechanism on a dark museum table, warm side lighting, realistic "
            "corrosion, deep shadows, no text, no logo, 16:9 composition."
        ),
        output_path="assets/images/generated/sample-antikythera-v01.png",
    )

    print(f"Saved image: {path}")