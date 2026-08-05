"""Create a standard Mahy Mythic Labs episode project structure."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

EPISODE_DIRECTORIES = (
    "research",
    "script",
    "storyboard",
    "assets/images",
    "assets/videos",
    "assets/audio",
    "audio/narration",
    "audio/music",
    "audio/sfx",
    "video",
    "thumbnail",
    "publishing",
    "review",
)

EPISODE_FILES = {
    "README.md": "# {episode_id} — {title}\n\n## Status\n\nDraft\n",
    "research/sources.md": "# Sources\n\n| Source | Claim Supported | Status |\n| --- | --- | --- |\n",
    "research/facts.md": "# Fact Sheet\n\n## Verified Facts\n\n",
    "script/script.md": "# Script\n\n## Hook\n\n",
    "script/narration.md": "# Narration\n\n",
    "storyboard/storyboard.md": "# Storyboard\n\n| Scene | Visual | Narration | Audio | Status |\n| --- | --- | --- | --- | --- |\n",
    "assets/asset_manifest.md": (
        "# Asset Manifest\n\n"
        "| Asset ID | Type | Source | Rights Status | Scene | Status |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    ),
    "audio/cue_sheet.md": "# Audio Cue Sheet\n\n| Time | Audio | Source | Status |\n| --- | --- | --- | --- |\n",
    "video/edit_plan.md": "# Edit Plan\n\n",
    "publishing/metadata.md": "# Publishing Metadata\n\n## Title\n\n## Description\n\n## Keywords\n\n",
    "review/episode_review.md": "# Episode Review\n\n## Quality Checklist\n\n- [ ] Research verified\n- [ ] Rights verified\n- [ ] Final export reviewed\n",
}


def create_episode(projects_root: Path, episode_id: str, title: str) -> Path:
    """Create missing episode folders and starter documents without overwriting."""
    episode_path = projects_root / episode_id

    for relative_directory in EPISODE_DIRECTORIES:
        (episode_path / relative_directory).mkdir(parents=True, exist_ok=True)

    for relative_file, template in EPISODE_FILES.items():
        file_path = episode_path / relative_file
        if not file_path.exists():
            file_path.write_text(
                template.format(episode_id=episode_id, title=title),
                encoding="utf-8",
            )

    return episode_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Mahy Mythic Labs episode structure."
    )
    parser.add_argument("episode_id", help="Example: EP001")
    parser.add_argument("title", help="Working episode title")
    parser.add_argument(
        "--projects-root",
        default="projects",
        help="Projects directory relative to the repository root.",
    )
    args = parser.parse_args()

    episode_path = create_episode(
        projects_root=Path(args.projects_root),
        episode_id=args.episode_id.upper(),
        title=args.title,
    )

    print(f"Episode structure ready: {episode_path}")


if __name__ == "__main__":
    main()