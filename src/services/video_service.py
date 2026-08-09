"""MoviePy Video Editing & Rendering Service for Mahy Mythic Labs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

logger = logging.getLogger("mahy.services.video")


class VideoRenderingService:
    """Automated MoviePy video assembly engine."""

    def render_episode_video(
        self,
        image_paths: List[str | Path],
        audio_path: str | Path,
        output_path: str | Path,
        *,
        fps: int = 24,
    ) -> Path:
        """Stitch images equally over narration audio duration and output .mp4."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        audio = AudioFileClip(str(audio_path))
        total_duration = audio.duration

        num_images = max(len(image_paths), 1)
        duration_per_image = total_duration / num_images

        clips = []
        for img in image_paths:
            clip = ImageClip(str(img)).with_duration(duration_per_image)
            clips.append(clip)

        final_video = concatenate_videoclips(clips, method="compose")
        final_video = final_video.with_audio(audio)

        logger.info(f"Rendering video to {output} (Duration: {total_duration:.2f}s)...")
        final_video.write_videofile(
            str(output),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )

        audio.close()
        final_video.close()
        return output


if __name__ == "__main__":
    service = VideoRenderingService()
    print("MoviePy Video Rendering Service initialized successfully!")
