"""
==============================================================================
Mahy Mythic Labs Studio OS

Environment Loader

Loads environment variables from .env files and resolves environment
placeholders inside configuration values.

Responsibilities
----------------
- Load .env file
- Read environment variables
- Resolve ${VAR_NAME} placeholders
- Validate required environment variables

Author : Mahy Mythic Labs
License: MIT
==============================================================================
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from src.config.defaults import (
    DEFAULT_ENCODING,
    DEFAULT_ENV_FILE,
)


class EnvironmentLoader:
    """
    Loads and manages environment variables.

    Example
    -------
    >>> env = EnvironmentLoader(project_root)
    >>> env.load()

    >>> api_key = env.get("OPENAI_API_KEY")

    >>> value = env.resolve("${OPENAI_API_KEY}")
    """

    ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")

    # ------------------------------------------------------------------ #

    def __init__(
        self,
        project_root: Path,
        env_file: str = DEFAULT_ENV_FILE,
    ) -> None:

        self.project_root = project_root

        self.env_path = project_root / env_file

        self.loaded = False

    # ------------------------------------------------------------------ #

    def load(self) -> None:
        """
        Load .env file into os.environ.

        Existing environment variables are preserved.
        """

        if self.loaded:
            return

        if not self.env_path.exists():
            self.loaded = True
            return

        with self.env_path.open(
            "r",
            encoding=DEFAULT_ENCODING,
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split("=", 1)

                key = key.strip()

                value = value.strip().strip('"').strip("'")

                os.environ.setdefault(key, value)

        self.loaded = True

    # ------------------------------------------------------------------ #

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """
        Get an environment variable.

        Example
        -------
        >>> env.get("OPENAI_API_KEY")
        """

        return os.getenv(key, default)

    # ------------------------------------------------------------------ #

    def require(
        self,
        key: str,
    ) -> str:
        """
        Get required environment variable.

        Raises
        ------
        EnvironmentError
            If variable does not exist.
        """

        value = os.getenv(key)

        if value is None:

            raise EnvironmentError(
                f"Required environment variable "
                f"'{key}' not found."
            )

        return value

    # ------------------------------------------------------------------ #

    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Check whether environment variable exists.
        """

        return key in os.environ

    # ------------------------------------------------------------------ #

    def set(
        self,
        key: str,
        value: str,
    ) -> None:
        """
        Set environment variable.
        """

        os.environ[key] = value

    # ------------------------------------------------------------------ #

    def resolve(
        self,
        value: Any,
    ) -> Any:
        """
        Resolve environment placeholders.

        Example
        -------
        "${OPENAI_API_KEY}"
        """

        if isinstance(value, dict):

            return {
                k: self.resolve(v)
                for k, v in value.items()
            }

        if isinstance(value, list):

            return [
                self.resolve(v)
                for v in value
            ]

        if not isinstance(value, str):
            return value

        def replace(match: re.Match[str]) -> str:

            variable = match.group(1)

            return os.getenv(variable, "")

        return self.ENV_PATTERN.sub(
            replace,
            value,
        )

    # ------------------------------------------------------------------ #

    def all(self) -> dict[str, str]:
        """
        Return all environment variables.
        """

        return dict(os.environ)

    # ------------------------------------------------------------------ #

    def reload(self) -> None:
        """
        Reload environment variables.
        """

        self.loaded = False

        self.load()

    # ------------------------------------------------------------------ #

    def __contains__(
        self,
        item: str,
    ) -> bool:

        return self.exists(item)

    # ------------------------------------------------------------------ #

    def __getitem__(
        self,
        item: str,
    ) -> str:

        return self.require(item)

    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"path='{self.env_path}')"
        )