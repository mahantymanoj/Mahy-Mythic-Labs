"""
==============================================================================
Mahy Mythic Labs Studio OS

YAML Configuration Loader

Responsibilities
----------------
- Load YAML files safely
- Merge multiple YAML files
- Resolve environment variables
- Preserve nested dictionaries
- Raise descriptive configuration errors

Author : Mahy Mythic Labs
License: MIT
==============================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.config.defaults import DEFAULT_ENCODING
from src.config.env_loader import EnvironmentLoader


class YAMLLoader:
    """
    Load and merge YAML configuration files.
    """

    # ------------------------------------------------------------------ #

    def __init__(
        self,
        env_loader: EnvironmentLoader,
    ) -> None:

        self.env_loader = env_loader

    # ------------------------------------------------------------------ #

    def load_file(
        self,
        path: str | Path,
    ) -> dict[str, Any]:
        """
        Load a single YAML file.
        """

        path = Path(path)

        if not path.exists():

            raise FileNotFoundError(
                f"Configuration file not found: {path}"
            )

        with path.open(
            "r",
            encoding=DEFAULT_ENCODING,
        ) as stream:

            data = yaml.safe_load(stream)

        if data is None:
            data = {}

        if not isinstance(data, dict):

            raise ValueError(
                f"{path.name} must contain a dictionary."
            )

        return self.env_loader.resolve(data)

    # ------------------------------------------------------------------ #

    def load_files(
        self,
        files: list[Path],
    ) -> dict[str, Any]:
        """
        Load and merge multiple YAML files.
        """

        config: dict[str, Any] = {}

        for file in files:

            yaml_data = self.load_file(file)

            config = self.merge(config, yaml_data)

        return config

    # ------------------------------------------------------------------ #

    def merge(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Deep merge dictionaries.

        override values always win.
        """

        merged = dict(base)

        for key, value in override.items():

            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):

                merged[key] = self.merge(
                    merged[key],
                    value,
                )

            else:

                merged[key] = value

        return merged

    # ------------------------------------------------------------------ #

    def load_directory(
        self,
        directory: str | Path,
    ) -> dict[str, Any]:
        """
        Load every YAML file in a directory.
        """

        directory = Path(directory)

        files = sorted(
            list(directory.glob("*.yaml"))
            + list(directory.glob("*.yml"))
        )

        return self.load_files(files)

    # ------------------------------------------------------------------ #

    def export(
        self,
        config: dict[str, Any],
        output_file: str | Path,
    ) -> None:
        """
        Save configuration to YAML.
        """

        output = Path(output_file)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output.open(
            "w",
            encoding=DEFAULT_ENCODING,
        ) as stream:

            yaml.safe_dump(
                config,
                stream,
                sort_keys=False,
                allow_unicode=True,
            )

    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}()"
        )