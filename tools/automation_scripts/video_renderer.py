"""CLI script to render an episode project folder into a final video."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.services.video_service import VideoRenderingService


def render_episode(episode_dir: Path) -> Path:
    """Read generated assets from episode directory and render final video."""
    images_dir = episode_dir / "assets/images"
    audio_path = episode_dir / "audio/narration/narration.mp3"
    output_path = episode_dir / "video/final_export.mp4"

    if not audio_path.exists():
        raise FileNotFoundError(f"Narration audio not found: {audio_path}")

    image_paths = sorted(list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")))
    if not image_paths:
        raise FileNotFoundError(f"No scene images found in: {images_dir}")

    service = VideoRenderingService()
    return service.render_episode_video(
        image_paths=image_paths,
        audio_path=audio_path,
        output_path=output_path,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Mahy Mythic Labs episode video.")
    parser.add_argument("episode_id", help="Example: EP001")
    parser.add_argument("--projects-root", default="projects", help="Projects root folder")
    args = parser.parse_args()

    ep_dir = Path(args.projects_root) / args.episode_id.upper()
    output = render_episode(ep_dir)
    print(f"✅ Video export complete: {output}")


if __name__ == "__main__":
    main()
