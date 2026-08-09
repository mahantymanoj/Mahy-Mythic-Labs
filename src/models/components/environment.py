"""
src/models/components/environment.py

Reusable environment configuration for Studio OS.

The environment defines the world in which a shot or scene takes
place. It includes location, historical era, weather, atmosphere,
architecture, terrain, vegetation, and visual ambience.

Author
------
Mahy Mythic Labs
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from src.models.base import ValueModel


EnvironmentType = Literal[
    "indoor",
    "outdoor",
    "underwater",
    "space",
    "mythological",
    "dream",
]

TerrainType = Literal[
    "mountain",
    "forest",
    "desert",
    "jungle",
    "grassland",
    "river",
    "ocean",
    "village",
    "city",
    "temple",
    "palace",
    "battlefield",
    "cave",
]

WeatherType = Literal[
    "clear",
    "cloudy",
    "rain",
    "storm",
    "snow",
    "fog",
    "mist",
    "windy",
]

SeasonType = Literal[
    "spring",
    "summer",
    "monsoon",
    "autumn",
    "winter",
]

AtmosphereType = Literal[
    "peaceful",
    "mystical",
    "epic",
    "dark",
    "tense",
    "sacred",
    "royal",
    "ancient",
    "divine",
]

TimeOfDay = Literal[
    "sunrise",
    "morning",
    "afternoon",
    "sunset",
    "night",
]

ArchitectureStyle = Literal[
    "indian_ancient",
    "greek",
    "roman",
    "egyptian",
    "medieval",
    "modern",
    "futuristic",
    "none",
]


class EnvironmentSettings(ValueModel):
    """
    Reusable environment description for cinematic generation.

    Shared across

    - Shot
    - Scene
    - Storyboard
    - AI prompt generation
    """

    name: str = Field(
        default="Unknown",
        description="Environment name.",
    )

    location: str = Field(
        default="Unknown",
        description="Physical location.",
    )

    historical_era: str = Field(
        default="Present",
        description="Historical era.",
    )

    environment_type: EnvironmentType = Field(
        default="outdoor",
    )

    terrain: TerrainType = Field(
        default="forest",
    )

    architecture: ArchitectureStyle = Field(
        default="none",
    )

    weather: WeatherType = Field(
        default="clear",
    )

    season: SeasonType = Field(
        default="summer",
    )

    time_of_day: TimeOfDay = Field(
        default="morning",
    )

    atmosphere: AtmosphereType = Field(
        default="peaceful",
    )

    vegetation: str = Field(
        default="natural vegetation",
        description="Vegetation description.",
    )

    water_body: str | None = Field(
        default=None,
        description="River, lake, ocean, waterfall, etc.",
    )

    sky_description: str = Field(
        default="clear blue sky",
    )

    background_description: str = Field(
        default="cinematic natural background",
    )

    temperature_celsius: float | None = Field(
        default=None,
        ge=-100,
        le=100,
    )

    population_density: str = Field(
        default="medium",
        description="Sparse, medium, dense.",
    )

    historical_accuracy: bool = Field(
        default=True,
        description="Maintain historical authenticity.",
    )

    mythical_elements: bool = Field(
        default=False,
        description="Allow mythological additions.",
    )

    cinematic_enhancement: bool = Field(
        default=True,
        description="Allow cinematic enhancement.",
    )

    @property
    def prompt(self) -> str:
        """
        Build reusable prompt fragment.
        """

        parts = [
            self.location,
            self.historical_era,
            self.environment_type,
            self.terrain,
            self.weather,
            self.time_of_day,
            self.atmosphere,
        ]

        if self.architecture != "none":
            parts.append(f"{self.architecture} architecture")

        if self.water_body:
            parts.append(self.water_body)

        parts.append(self.sky_description)
        parts.append(self.background_description)

        return ", ".join(parts)

    def is_historical(self) -> bool:
        """
        Whether historical accuracy is required.
        """
        return self.historical_accuracy

    def is_mythological(self) -> bool:
        """
        Whether mythical elements are allowed.
        """
        return self.mythical_elements

    def is_outdoor(self) -> bool:
        """
        True if the environment is outdoors.
        """
        return self.environment_type == "outdoor"
    