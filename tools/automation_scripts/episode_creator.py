"""Create a standard Mahy Mythic Labs episode project structure and optionally run production pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.enums import EpisodeFormat
from src.engine.director import MasterDirector
from src.models.episode import EpisodeConfig
from tools.automation_scripts.video_renderer import render_episode

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
    "audio/cue_sheet.md": "# Audio Cue Sheet\n\n| Time | Audio | Source | Status |\n| --- | --- | --- |\n",
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
        description="Create a Mahy Mythic Labs episode structure and run zero-cost production."
    )
    parser.add_argument("episode_id", help="Example: EP001")
    parser.add_argument("title", help="Working episode title")
    parser.add_argument("--domain", default="astronomy", help="Knowledge domain: astronomy, mythology, history, science")
    parser.add_argument("--format", choices=["short", "documentary"], default="short", help="Episode format")
    parser.add_argument("--duration", type=int, default=60, help="Target duration in seconds")
    parser.add_argument("--projects-root", default="projects", help="Projects directory relative to repository root.")
    parser.add_argument("--run-pipeline", action="store_true", help="Automatically run zero-cost research, script, TTS, and image pipeline")
    parser.add_argument("--render", action="store_true", help="Render final video export after pipeline run")
    args = parser.parse_args()

    projects_path = Path(args.projects_root)
    ep_id = args.episode_id.upper()
    episode_path = create_episode(
        projects_root=projects_path,
        episode_id=ep_id,
        title=args.title,
    )

    print(f"[OK] Episode structure ready: {episode_path}")

    if args.run_pipeline:
        ep_format = EpisodeFormat.SHORT_9_16 if args.format == "short" else EpisodeFormat.DOCUMENTARY_16_9
        config = EpisodeConfig(
            episode_id=ep_id,
            title=args.title,
            domain=args.domain,
            format=ep_format,
            target_duration_seconds=args.duration,
        )

        print(f"[RUN] Running MasterDirector zero-cost pipeline for {ep_id}...")
        director = MasterDirector(config, projects_root=projects_path)
        success = director.run()
        if not success:
            print("[FAIL] Pipeline failed. Check state.json logs.")
            sys.exit(1)
        print("[SUCCESS] Pipeline completed successfully!")

        if args.render:
            print("[RENDER] Rendering final video export...")
            render_output = render_episode(episode_path)
            print(f"[COMPLETE] Final Video Exported: {render_output}")


if __name__ == "__main__":
    main()