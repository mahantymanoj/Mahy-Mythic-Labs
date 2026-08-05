"""Client for text-generation tasks in the Mahy Mythic Labs pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI

@dataclass
class LLMClient:
    """Generate structured production text with the OpenAI Responses API."""

    model: str = os.getenv("MAHY_LLM_MODEL", "gpt-5.6-terra")

    def __post_init__(self) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set.")
        self.client = OpenAI()

    def generate(self, prompt: str, *,
                 instructions: str,
                 verbosity: str = "medium",) -> str:
        """Return text output for a research, writing, or review task."""
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
            text={"verbosity": verbosity},
        )
        return response.output_text


if __name__ == "__main__":
    client = LLMClient()
    result = client.generate(
        "Create three evidence-led documentary episode ideas about ancient astronomy.",
        instructions=(
            "You are the Mahy Mythic Labs research and development assistant. "
            "Separate evidence from speculation. Return concise Markdown."
        ),
    )
    print(result)