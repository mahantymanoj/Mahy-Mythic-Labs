"""Client for text-generation tasks in the Mahy Mythic Labs pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from openai import OpenAI


@dataclass
class LLMClient:
    """Generate structured production text using the OpenAI Chat Completions API."""

    model: str = field(default_factory=lambda: os.getenv("MAHY_LLM_MODEL", "gpt-4o"))

    def __post_init__(self) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set.")
        self.client = OpenAI()

    def generate(
        self,
        prompt: str,
        *,
        instructions: str,
        temperature: float = 0.7,
    ) -> str:
        """Return text output for a research, writing, or review task."""
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("OpenAI returned an empty response.")
        return content


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
