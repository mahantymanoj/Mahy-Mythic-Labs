"""Central configuration for Mahy Mythic Labs tools."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_project_environment() -> None:
    """Load environment variables from an optional repository-root .env file."""
    project_root = Path(
        os.getenv("MAHY_PROJECT_ROOT", Path.cwd())
    ).resolve()

    load_dotenv(project_root / ".env")


def get_project_root() -> Path:
    """Return the configured Mahy Mythic Labs repository root."""
    return Path(
        os.getenv("MAHY_PROJECT_ROOT", Path.cwd())
    ).resolve()


def get_required_setting(name: str) -> str:
    """Return a required environment variable without exposing its value."""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required configuration value is missing: {name}. "
            "Set it as an environment variable or in a local .env file."
        )

    return value


def get_optional_setting(name: str, default: str = "") -> str:
    """Return an optional environment variable or its default value."""
    return os.getenv(name, default)


load_project_environment()