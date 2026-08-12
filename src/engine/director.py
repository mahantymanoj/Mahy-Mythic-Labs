"""Master Director Orchestrator for Mahy Mythic Labs."""

from __future__ import annotations

from pathlib import Path

from src.enums import EpisodeFormat
from src.engine.context import PipelineContext
from src.engine.pipeline import Pipeline, PipelineStage
from src.engine.state import StateManager
from src.models.episode import EpisodeConfig
from src.providers.provider_factory import ProviderFactory


class ResearchStage(PipelineStage):
    def __init__(self) -> None:
        super().__init__("research")

    def execute(self, ctx: PipelineContext) -> bool:
        llm = ProviderFactory.get_llm_provider()
        prompt = f"Conduct documentary research on topic: {ctx.config.title} in domain {ctx.config.domain}."
        facts = llm.generate(prompt, instructions="Provide 5 verified facts with historical/scientific context.")
        
        research_file = ctx.get_path("research/facts.md")
        research_file.write_text(f"# Research: {ctx.config.title}\n\n{facts}\n", encoding="utf-8")
        ctx.state.stage_data["research_facts"] = facts
        return True


class ScriptStage(PipelineStage):
    def __init__(self) -> None:
        super().__init__("script")

    def execute(self, ctx: PipelineContext) -> bool:
        llm = ProviderFactory.get_llm_provider()
        prompt = f"Write a video script for '{ctx.config.title}'. Target duration: {ctx.config.target_duration_seconds}s."
        script_text = llm.generate(prompt, instructions="Write Hook, Main Narration, and Call To Action.")

        script_file = ctx.get_path("script/script.md")
        script_file.write_text(f"# Script: {ctx.config.title}\n\n{script_text}\n", encoding="utf-8")

        # Also write clean narration text
        narration_file = ctx.get_path("script/narration.md")
        narration_file.write_text(script_text, encoding="utf-8")

        ctx.state.stage_data["narration_text"] = script_text
        return True


class NarrationStage(PipelineStage):
    def __init__(self) -> None:
        super().__init__("narration")

    def execute(self, ctx: PipelineContext) -> bool:
        audio_provider = ProviderFactory.get_audio_provider()
        narration_text = ctx.state.stage_data.get("narration_text", f"Exploring the mysteries of {ctx.config.title}.")
        
        output_file = ctx.get_path("audio/narration/narration.mp3")
        audio_provider.generate(narration_text, output_file, voice=ctx.config.voice_name)
        
        ctx.state.stage_data["narration_audio_path"] = str(output_file)
        return True


class StoryboardStage(PipelineStage):
    def __init__(self) -> None:
        super().__init__("storyboard")

    def execute(self, ctx: PipelineContext) -> bool:
        image_provider = ProviderFactory.get_image_provider()

        width = 1080 if ctx.config.format == EpisodeFormat.SHORT_9_16 else 1920
        height = 1920 if ctx.config.format == EpisodeFormat.SHORT_9_16 else 1080

        # Generate 3 visual scenes for the episode
        for i in range(1, 4):
            prompt = f"{ctx.config.title}, scene {i}, {ctx.config.style_prompt}"
            img_file = ctx.get_path(f"assets/images/scene_{i:02d}.png")
            image_provider.generate(prompt, img_file, width=width, height=height, seed=40 + i)

        storyboard_file = ctx.get_path("storyboard/storyboard.md")
        storyboard_file.write_text(
            f"# Storyboard: {ctx.config.title}\n\nGenerated 3 scene assets in assets/images/\n",
            encoding="utf-8"
        )
        return True


class MasterDirector:
    """Master Director executing the episode creation pipeline."""

    def __init__(self, config: EpisodeConfig, projects_root: Path = Path("projects")) -> None:
        state_file = projects_root / config.episode_id / "state.json"
        state = StateManager.load(state_file, config.episode_id)

        self.ctx = PipelineContext(config=config, state=state, projects_root=projects_root)
        self.pipeline = Pipeline(self.ctx)

        # Build pipeline DAG stages
        self.pipeline.add_stage(ResearchStage())
        self.pipeline.add_stage(ScriptStage())
        self.pipeline.add_stage(NarrationStage())
        self.pipeline.add_stage(StoryboardStage())

    def run(self) -> bool:
        return self.pipeline.run()
